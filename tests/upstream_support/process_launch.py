"""Launch upstream test children with posix_spawn on macOS, never fork.

Apple Network.framework initializes background threads during URL/proxy access.
The crash reports show its atfork child handler crashing before exec. Selecting
posix_spawn avoids copying that unsafe runtime state into the child. Explicit
spawn file actions close extra descriptors, including pytest's inherited captures.
"""

import ctypes
import errno
import os
import shutil
import signal
import stat
import subprocess
import sys

_OriginalPopen = subprocess.Popen


class Popen(_OriginalPopen):
    def __init__(self, args, *positional, **kwargs):
        if sys.platform == "darwin":
            if positional:
                raise TypeError("Use keyword subprocess options in the upstream harness")
            if isinstance(args, (str, bytes)) or kwargs.get("shell"):
                raise TypeError("The upstream harness requires an argument array")
            if kwargs.get("pass_fds"):
                raise RuntimeError("The upstream harness does not inherit extra descriptors")
            args = list(args)
            self._spawn_directory = kwargs.pop("cwd", None)
            executable = kwargs.get("executable") or args[0]
            environment = kwargs.get("env")
            if self._spawn_directory is not None:
                executable = self._directory_executable(executable, environment)
            else:
                executable = shutil.which(
                    executable, path=environment.get("PATH") if environment else None
                )
            if executable is None:
                raise FileNotFoundError(args[0])
            kwargs["executable"] = executable
            kwargs["close_fds"] = False
        super().__init__(args, **kwargs)

    def _directory_executable(self, executable, environment):
        directory = os.fsdecode(self._spawn_directory)
        if not os.path.isabs(directory):
            directory = os.path.join(os.getcwd(), directory)
        if not stat.S_ISDIR(os.stat(directory).st_mode):
            raise NotADirectoryError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), directory)
        if not os.access(directory, os.X_OK):
            raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), directory)
        self._spawn_directory = directory
        executable = os.fsdecode(executable)
        if os.path.dirname(executable):
            return os.path.join(directory, executable)
        # bounded: the process PATH, not any graph or workspace relation.
        paths = [os.path.join(directory, path) for path in os.get_exec_path(environment)]
        result = shutil.which(executable, path=os.pathsep.join(paths))
        if result is None and any(os.path.exists(os.path.join(path, executable)) for path in paths):
            raise PermissionError(errno.EACCES, os.strerror(errno.EACCES), executable)
        return result

    def _posix_spawn(self, args, executable, env, restore_signals, *pipe_args):
        # Python 3.13 adds close_fds before the six pipe descriptors.
        if len(pipe_args) not in (6, 7):
            raise RuntimeError("Unsupported Python posix_spawn pipe contract")
        p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite = pipe_args[-6:]
        actions = [
            (os.POSIX_SPAWN_DUP2, fd, target)
            for fd, target in ((p2cread, 0), (c2pwrite, 1), (errwrite, 2))
            if fd != -1
        ]
        for entry in os.listdir("/dev/fd"):
            fd = int(entry)
            if fd < 3:
                continue
            try:
                if not os.get_inheritable(fd):
                    continue
            except OSError as error:
                if error.errno == errno.EBADF:
                    continue  # The /dev/fd directory iterator has already closed.
                raise
            actions.append((os.POSIX_SPAWN_CLOSE, fd))
        options = {"file_actions": actions}
        if restore_signals:
            options["setsigdef"] = [
                getattr(signal, name)
                for name in ("SIGPIPE", "SIGXFZ", "SIGXFSZ")
                if hasattr(signal, name)
            ]
        if env is None:
            env = os.environ
        if sys.platform == "darwin" and self._spawn_directory is not None:
            self.pid = _DarwinSpawn(executable).spawn(
                args, env, actions, options.get("setsigdef", []), self._spawn_directory
            )
        else:
            self.pid = os.posix_spawn(executable, args, env, **options)
        self._child_created = True
        self._close_pipe_fds(p2cread, p2cwrite, c2pread, c2pwrite, errread, errwrite)

    def _execute_child(self, *args, **kwargs):
        if sys.platform != "darwin":
            return super()._execute_child(*args, **kwargs)
        # If a future Python version or unsupported option prevents spawn,
        # fail before entering fork. No retry through the unsafe path.
        import inspect

        options = (
            inspect.signature(_OriginalPopen._execute_child).bind(self, *args, **kwargs).arguments
        )
        if (
            not subprocess._USE_POSIX_SPAWN
            or options.get("preexec_fn") is not None
            or options.get("cwd") is not None
            or options.get("start_new_session")
            or options.get("process_group", -1) != -1
            or any(options.get(k) is not None for k in ("gid", "gids", "uid"))
            or options.get("umask", -1) >= 0
        ):
            raise RuntimeError("Subprocess options require unsafe fork on macOS")
        return super()._execute_child(*args, **kwargs)


class _DarwinSpawn:
    """Use Darwin's public opaque spawn handles for its native chdir action."""

    def __init__(self, executable):
        if sys.platform != "darwin":
            raise RuntimeError("Darwin spawn ABI requires macOS")
        self.executable = executable
        self.library = ctypes.CDLL(None, use_errno=True)
        handle = ctypes.POINTER(ctypes.c_void_p)
        signals = ctypes.POINTER(ctypes.c_uint32)
        strings = ctypes.POINTER(ctypes.c_char_p)
        # Darwin spawn.h: handles are void*, pid_t is int, sigset_t is uint32.
        # addchdir_np is available since macOS 10.15, including the CI macOS 15.
        bindings = (
            (
                "posix_spawn",
                [ctypes.POINTER(ctypes.c_int), ctypes.c_char_p, handle, handle, strings, strings],
            ),
            ("posix_spawn_file_actions_init", [handle]),
            ("posix_spawn_file_actions_destroy", [handle]),
            ("posix_spawn_file_actions_addchdir_np", [handle, ctypes.c_char_p]),
            ("posix_spawn_file_actions_adddup2", [handle, ctypes.c_int, ctypes.c_int]),
            ("posix_spawn_file_actions_addclose", [handle, ctypes.c_int]),
            ("posix_spawnattr_init", [handle]),
            ("posix_spawnattr_destroy", [handle]),
            ("posix_spawnattr_setsigdefault", [handle, signals]),
            ("posix_spawnattr_setflags", [handle, ctypes.c_short]),
            ("sigemptyset", [signals]),
            ("sigaddset", [signals, ctypes.c_int]),
        )
        for name, arguments in bindings:
            function = getattr(self.library, name)
            function.argtypes = arguments
            function.restype = ctypes.c_int

    def _check(self, result):
        if result:
            raise OSError(result, os.strerror(result), self.executable)

    @staticmethod
    def _bytes(value):
        result = os.fsencode(value)
        if b"\0" in result:
            raise ValueError("Embedded null byte in subprocess input")
        return result

    def _environment(self, environment):
        result = []
        for name, value in environment.items():
            name = self._bytes(name)
            if b"=" in name:
                raise ValueError("Illegal subprocess environment variable name")
            result.append(name + b"=" + self._bytes(value))
        return result

    def _signals(self, attributes, signals):
        if not signals:
            return
        mask = ctypes.c_uint32()
        self._signal_call("sigemptyset", ctypes.byref(mask))
        for number in signals:
            self._signal_call("sigaddset", ctypes.byref(mask), number)
        self._check(
            self.library.posix_spawnattr_setsigdefault(ctypes.byref(attributes), ctypes.byref(mask))
        )
        # POSIX_SPAWN_SETSIGDEF from Darwin's public sys/spawn.h.
        self._check(self.library.posix_spawnattr_setflags(ctypes.byref(attributes), 0x0004))

    def _signal_call(self, name, *arguments):
        result = getattr(self.library, name)(*arguments)
        if result:
            number = ctypes.get_errno()
            raise OSError(
                number, f"{name} failed ({result}): {os.strerror(number)}", self.executable
            )

    def _actions(self, handle, directory, actions):
        self._check(
            self.library.posix_spawn_file_actions_addchdir_np(
                ctypes.byref(handle), self._bytes(directory)
            )
        )
        for action in actions:
            if action[0] == os.POSIX_SPAWN_DUP2:
                result = self.library.posix_spawn_file_actions_adddup2(
                    ctypes.byref(handle), *action[1:]
                )
            elif action[0] == os.POSIX_SPAWN_CLOSE:
                result = self.library.posix_spawn_file_actions_addclose(
                    ctypes.byref(handle), action[1]
                )
            else:
                raise RuntimeError("Unsupported native spawn file action")
            self._check(result)

    def spawn(self, arguments, environment, actions, signals, directory):
        # bounded: one process argv/environment; buffers live through the C call.
        words = [self._bytes(value) for value in arguments]
        values = self._environment(environment)
        argv = (ctypes.c_char_p * (len(words) + 1))(*words, None)
        envp = (ctypes.c_char_p * (len(values) + 1))(*values, None)
        file_actions = ctypes.c_void_p()
        attributes = ctypes.c_void_p()
        self._check(self.library.posix_spawn_file_actions_init(ctypes.byref(file_actions)))
        try:
            self._check(self.library.posix_spawnattr_init(ctypes.byref(attributes)))
            try:
                self._actions(file_actions, directory, actions)
                self._signals(attributes, signals)
                pid = ctypes.c_int()
                self._check(
                    self.library.posix_spawn(
                        ctypes.byref(pid),
                        self._bytes(self.executable),
                        ctypes.byref(file_actions),
                        ctypes.byref(attributes),
                        argv,
                        envp,
                    )
                )
                return pid.value
            finally:
                self._check(self.library.posix_spawnattr_destroy(ctypes.byref(attributes)))
        finally:
            self._check(self.library.posix_spawn_file_actions_destroy(ctypes.byref(file_actions)))


def install():
    if sys.platform != "darwin":
        return
    subprocess.Popen = Popen

    def forbidden(*args, **kwargs):
        raise RuntimeError("The upstream harness forbids fork on macOS; use posix_spawn")

    subprocess._fork_exec = forbidden

"""Launch upstream test children with posix_spawn on macOS, never fork.

Apple Network.framework initializes background threads during URL/proxy access.
The crash reports show its atfork child handler crashing before exec. Selecting
posix_spawn avoids copying that unsafe runtime state into the child. Explicit
spawn file actions close extra descriptors, including pytest's inherited captures.
"""

import errno
import os
import shutil
import signal
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
            executable = kwargs.get("executable") or args[0]
            environment = kwargs.get("env")
            executable = shutil.which(
                executable, path=environment.get("PATH") if environment else None
            )
            if executable is None:
                raise FileNotFoundError(args[0])
            kwargs["executable"] = executable
            kwargs["close_fds"] = False
        super().__init__(args, **kwargs)

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


def install():
    if sys.platform != "darwin":
        return
    subprocess.Popen = Popen

    def forbidden(*args, **kwargs):
        raise RuntimeError("The upstream harness forbids fork on macOS; use posix_spawn")

    subprocess._fork_exec = forbidden

"""Exercise subprocess launch after macOS framework initialization without fork."""

import importlib.util
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

SUPPORT = Path(__file__).parent / "upstream_support"


def load_launcher():
    spec = importlib.util.spec_from_file_location("process_launch", SUPPORT / "process_launch.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
def test_cwd_launch_preserves_argv_stdin_pid_and_exit_without_fork(tmp_path, monkeypatch):
    monkeypatch.setattr(subprocess, "_fork_exec", lambda *args: pytest.fail("unsafe fork"))
    directory = tmp_path / "working ; '$ directory"
    directory.mkdir()
    arguments = ["literal ; $(touch SHOULD_NOT_EXIST)", "quoted ' \" $ value"]
    code = (
        "import json,os,sys; "
        "print(json.dumps([os.getcwd(),sys.argv[1:],sys.stdin.read(),os.getpid()])); sys.exit(7)"
    )
    with load_launcher().Popen(
        [sys.executable, "-I", "-S", "-B", "-c", code, *arguments],
        cwd=directory,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        stdout, stderr = process.communicate("input ; $ text", timeout=10)
        assert process.returncode == 7
        assert json.loads(stdout) == [
            str(directory.resolve()),
            arguments,
            "input ; $ text",
            process.pid,
        ]
        assert stderr == ""
    assert not (directory / "SHOULD_NOT_EXIST").exists()


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
@pytest.mark.parametrize(
    "locale",
    [
        {"LC_ALL": "C", "PYTHONCOERCECLOCALE": "1"},
        {"LANG": "C", "PYTHONCOERCECLOCALE": "1", "PYTHONHOME": "/not-an-interpreter"},
        {"LC_ALL": "C", "PYTHONCOERCECLOCALE": "0", "PYTHONPATH": "/not-an-import"},
    ],
)
def test_cwd_launch_preserves_the_complete_supplied_environment(tmp_path, locale, monkeypatch):
    monkeypatch.setattr(subprocess, "_fork_exec", lambda *args: pytest.fail("unsafe fork"))
    launcher = load_launcher()
    environment = {"PATH": os.defpath, "VALUE": "literal ; '$ value", **locale}
    results = []
    for options in ({}, {"cwd": tmp_path}):
        with launcher.Popen(
            ["/usr/bin/env"], env=environment, stdout=subprocess.PIPE, text=True, **options
        ) as process:
            stdout, _ = process.communicate(timeout=10)
            assert process.returncode == 0
            results.append(dict(line.split("=", 1) for line in stdout.splitlines()))
    assert results[0] == results[1]


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
@pytest.mark.parametrize("restore", [True, False])
@pytest.mark.parametrize("inherited", [signal.SIG_DFL, signal.SIG_IGN])
def test_cwd_launch_preserves_signal_disposition(tmp_path, monkeypatch, restore, inherited):
    monkeypatch.setattr(subprocess, "_fork_exec", lambda *args: pytest.fail("unsafe fork"))
    launcher = load_launcher()
    previous = signal.signal(signal.SIGPIPE, inherited)
    try:
        statuses = []
        for options in ({}, {"cwd": tmp_path}):
            with launcher.Popen(
                ["/bin/sh", "-c", 'kill -PIPE "$$"; exit 19'], restore_signals=restore, **options
            ) as process:
                statuses.append(process.wait(timeout=10))
        assert statuses == [-signal.SIGPIPE if restore or inherited == signal.SIG_DFL else 19] * 2
    finally:
        signal.signal(signal.SIGPIPE, previous)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
@pytest.mark.parametrize("invalid", ["cwd", "executable", "permission"])
def test_cwd_launch_rejects_known_invalid_inputs_before_spawn(tmp_path, monkeypatch, invalid):
    monkeypatch.setattr(
        os, "posix_spawn", lambda *args, **kwargs: pytest.fail("spawned invalid input")
    )
    directory = tmp_path
    command = sys.executable
    expected = FileNotFoundError
    if invalid == "cwd":
        directory = tmp_path / "missing-directory"
    elif invalid == "executable":
        command = str(tmp_path / "missing-executable")
    else:
        target = tmp_path / "nonexecutable"
        target.write_text("#!/bin/sh\nexit 0\n")
        target.chmod(0o600)
        command = str(target)
        expected = PermissionError
    with pytest.raises(expected):
        load_launcher().Popen([command], cwd=directory)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
@pytest.mark.parametrize("options", [{"start_new_session": True}, {"pass_fds": (1,)}])
def test_cwd_launch_keeps_unsupported_options_as_hard_errors(tmp_path, monkeypatch, options):
    monkeypatch.setattr(subprocess, "_fork_exec", lambda *args: pytest.fail("unsafe fork"))
    with pytest.raises(RuntimeError, match="unsafe fork|does not inherit"):
        load_launcher().Popen([sys.executable, "-c", "pass"], cwd=tmp_path, **options)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
@pytest.mark.parametrize(
    "invalid", ["argv", "executable", "cwd", "env-name", "env-value", "env-equals"]
)
def test_native_spawn_rejects_unrepresentable_c_strings(tmp_path, monkeypatch, invalid):
    launcher = load_launcher()
    original = launcher.ctypes.CDLL

    def library(*args, **kwargs):
        result = original(*args, **kwargs)

        def forbidden(*arguments):
            pytest.fail("invalid input reached native spawn")

        result.posix_spawn = forbidden
        return result

    monkeypatch.setattr(launcher.ctypes, "CDLL", library)
    arguments = [sys.executable, "-I", "-S", "-B", "-c", "pass"]
    options = {"cwd": tmp_path, "env": {"PATH": os.defpath}}
    if invalid == "argv":
        arguments.append("word\0hidden")
    elif invalid == "executable":
        options["executable"] = sys.executable + "\0hidden"
    elif invalid == "cwd":
        options["cwd"] = str(tmp_path) + "\0hidden"
    elif invalid == "env-name":
        options["env"]["BAD\0NAME"] = "value"
    elif invalid == "env-value":
        options["env"]["NAME"] = "value\0hidden"
    else:
        options["env"]["BAD=NAME"] = "value"
    with pytest.raises(ValueError):
        launcher.Popen(arguments, **options)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
def test_native_spawn_preserves_surrogateescaped_arguments(tmp_path):
    launcher = load_launcher()
    word = b"word\xff"
    for argument in (word, os.fsdecode(word)):
        for options in ({}, {"cwd": tmp_path}):
            with launcher.Popen(
                ["/usr/bin/printf", "%s", argument], stdout=subprocess.PIPE, **options
            ) as process:
                stdout, _ = process.communicate(timeout=10)
                assert process.returncode == 0
                assert stdout == word


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
def test_native_spawn_preserves_surrogateescaped_environment(tmp_path):
    launcher = load_launcher()
    raw = {b"PATH": os.fsencode(os.defpath), b"KEY\xff": b"value\xfe"}
    decoded = {os.fsdecode(name): os.fsdecode(value) for name, value in raw.items()}
    for environment in (raw, decoded):
        outputs = []
        for options in ({}, {"cwd": tmp_path}):
            with launcher.Popen(
                ["/usr/bin/env"], env=environment, stdout=subprocess.PIPE, **options
            ) as process:
                stdout, _ = process.communicate(timeout=10)
                assert process.returncode == 0
                outputs.append(stdout)
        assert outputs[0] == outputs[1]
        assert b"KEY\xff=value\xfe\n" in outputs[1]


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
def test_launch_never_calls_fork_and_preserves_output_and_exit_status(monkeypatch):
    # Reproduce the unsafe branch without allowing it to create another crash.
    def forbidden_fork(*args, **kwargs):
        raise AssertionError("unsafe fork selected")

    monkeypatch.setattr(subprocess, "_fork_exec", forbidden_fork)
    launcher = load_launcher()
    with launcher.Popen(
        [
            sys.executable,
            "-c",
            'import sys; print("output"); print("error", file=sys.stderr); sys.exit(7)',
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == 7
    assert stdout == "output\n"
    assert stderr == "error\n"


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
def test_launch_closes_inheritable_descriptors(tmp_path):
    launcher = load_launcher()
    with (tmp_path / "private").open("w") as stream:
        os.set_inheritable(stream.fileno(), True)
        try:
            script = f"import os,sys\ntry: os.fstat({stream.fileno()})\nexcept OSError: sys.exit(0)\nsys.exit(3)"
            with launcher.Popen([sys.executable, "-c", script]) as process:
                assert process.wait(timeout=10) == 0
        finally:
            os.set_inheritable(stream.fileno(), False)


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS subprocess policy")
def test_launch_after_network_frameworks_and_background_thread(monkeypatch):
    import threading
    import urllib.request

    def forbidden_fork(*args, **kwargs):
        raise AssertionError("unsafe fork selected after network initialization")

    monkeypatch.setattr(subprocess, "_fork_exec", forbidden_fork)
    urllib.request.getproxies()
    done = threading.Event()
    thread = threading.Thread(target=done.wait)
    thread.start()
    try:
        with load_launcher().Popen([sys.executable, "-c", "pass"]) as process:
            assert process.wait(timeout=10) == 0
    finally:
        done.set()
        thread.join()

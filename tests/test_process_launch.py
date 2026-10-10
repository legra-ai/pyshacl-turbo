"""Exercise subprocess launch after macOS framework initialization without fork."""

import importlib.util
import os
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

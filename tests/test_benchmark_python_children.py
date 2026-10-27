"""Isolated benchmark children must not mutate installed/source bytecode trees."""

import json
from pathlib import Path

from test_literal_fanout_benchmark import load


def assert_python_flags(argv):
    assert list(map(str, argv[1:3])) == ["-I", "-B"]
    assert str(argv[3]).endswith(".py")


def test_companion_launch_disables_bytecode_before_script(monkeypatch):
    from upstream_support import process_launch

    bench = load("companions")
    calls = []

    class Process:
        returncode = 0

        def __init__(self, argv, **_):
            calls.append(argv)

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def communicate(self, *, timeout):
            assert timeout == 5
            return '{"actual":true}', ""

    monkeypatch.setattr(process_launch, "Popen", Process)
    assert bench.launch({"operation": "owlrl"}, 1, "time", 5) == {"actual": True}
    assert_python_flags(calls[0])


def test_release_setup_identity_disables_bytecode_before_script(tmp_path, monkeypatch):
    bench = load("releases")
    calls = []

    def command(argv, **_):
        calls.append(argv)
        if "init" in argv:
            project = Path(argv[-1])
            project.mkdir(parents=True)
            (project / "pyproject.toml").write_text('[project]\nname="fixture"\n')
        if "sync" in argv:
            (tmp_path / "fixture/uv.lock").write_text("version = 1\n")
        return json.dumps({"packages": {}}) if "--identity" in argv else ""

    monkeypatch.setattr(bench, "command", command)
    bench.setup({"id": "fixture", "requirements": {}}, tmp_path, None, "3.13.16")
    assert_python_flags(next(argv for argv in calls if "--identity" in argv))

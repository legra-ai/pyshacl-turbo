"""An upstream case keeps its identity when the checkout moves machines."""

import importlib.util
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def portable_id():
    path = Path(__file__).parent / "upstream_support/case_ids.py"
    spec = importlib.util.spec_from_file_location("case_ids", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.portable_id


@pytest.mark.parametrize(
    "root",
    [
        "/Users/a/Work/pyshacl-turbo",
        "/home/runner/work/pyshacl-turbo/pyshacl-turbo",
        "/tmp/with space",
    ],
)
def test_absolute_and_file_uri_parameters_become_repository_relative(portable_id, root):
    checkout = Path(root)
    first = "vendor/pyshacl/test/resources/core/one.ttl"
    second = "vendor/pyshacl/test/resources/core/two.ttl"
    name = "test/test_sht_validate.py::test_sht_all"
    original = f"{name}[{checkout.as_uri()}/{first}-{checkout}/{second}-1]"
    assert portable_id(original, checkout) == f"{name}[{first}-{second}-1]"


def test_case_parameters_and_external_paths_are_not_erased(portable_id):
    checkout = Path("/tmp/repo")
    prefix = "test/example.py::test_case"
    for parameter in ("0", "1", "None", "other.ttl", "/tmp/external/file.ttl"):
        case = f"{prefix}[{parameter}]"
        assert portable_id(case, checkout) == case
    one = portable_id(f"{prefix}[/tmp/repo/vendor/one.ttl-0]", checkout)
    two = portable_id(f"{prefix}[/tmp/repo/vendor/one.ttl-1]", checkout)
    assert one != two


def test_upstream_runner_keeps_complete_long_parameter_ids(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    commands = []
    with monkeypatch.context() as patch:
        patch.setattr(sys, "argv", ["run_upstream.py", "--output", str(tmp_path / "report.json")])
        patch.setattr(
            subprocess,
            "run",
            lambda command, **kwargs: commands.append(command) or SimpleNamespace(returncode=0),
        )
        with pytest.raises(SystemExit) as exit_status:
            runpy.run_path(str(root / "scripts/run_upstream.py"), run_name="__main__")
    assert exit_status.value.code == 0
    options = []
    for index, argument in enumerate(commands[0]):
        if argument == "-o":
            options.extend(commands[0][index : index + 2])
    parameter = "file:///" + "long-checkout/" * 15 + "input.ttl"
    case = tmp_path / "test_parameter.py"
    case.write_text(
        "import pytest\n"
        f"@pytest.mark.parametrize('source', [{parameter!r}])\n"
        "def test_input(source):\n    assert source\n"
    )
    spec = importlib.util.spec_from_file_location(
        "case_launcher", root / "tests/upstream_support/process_launch.py"
    )
    launcher = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(launcher)
    process_type = launcher.Popen if sys.platform == "darwin" else subprocess.Popen
    with process_type(
        [sys.executable, "-I", "-B", "-m", "pytest", str(case), "--collect-only", "-q", *options],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        stdout, stderr = process.communicate(timeout=30)
    assert process.returncode == 0, stdout + stderr
    assert f"test_input[{parameter}]" in stdout

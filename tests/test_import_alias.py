"""The start-up alias serves ``import pyshacl`` and can be turned off (ADR 0049)."""

import importlib
import os
import runpy
import subprocess
import sys
from pathlib import Path

import pyshacl_turbo
import pyshacl_turbo_alias as hook
import pytest
from pyshacl_turbo import compat
from pyshacl_turbo_alias import PYSHACL, AliasFinder, AliasLoader, TurboAlias, TurboAliasError
from upstream_support.process_launch import Popen

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_FILES = ("__init__.py", "errors.py")


def alias_env(**values):
    env = {k: v for k, v in os.environ.items() if k not in {"PYSHACL_TURBO_ALIAS", "TURBO_ALIAS"}}
    env.update(values)
    return env


def python(code, env):
    with Popen(
        [sys.executable, "-c", code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    ) as process:
        out, err = process.communicate(timeout=120)
    return process.returncode, out.strip(), err


def test_the_pth_line_installs_the_alias():
    line = (ROOT / "python/pyshacl_turbo_alias.pth").read_text()
    assert line == "import pyshacl_turbo_alias; pyshacl_turbo_alias.install()\n"


def test_the_hook_module_defines_its_alias_without_engine_imports():
    # The interpreter imported the hook before coverage started; executing its
    # source again measures the start-up definitions themselves.
    namespace = runpy.run_path(hook.__file__, run_name="pyshacl_turbo_alias_fresh")
    assert namespace["PYSHACL"].switch == "PYSHACL_TURBO_ALIAS"
    assert namespace["SHARED_SWITCH"] == "TURBO_ALIAS"
    assert namespace["TYPE_CHECKING"] is False


def test_the_alias_targets_the_compatibility_package():
    assert PYSHACL.target_name("pyshacl") == "pyshacl_turbo.compat"
    assert PYSHACL.target_name("pyshacl.rdfutil.load") == "pyshacl_turbo.compat.rdfutil.load"
    assert PYSHACL.target_name("pyshacl_turbo") is None
    assert PYSHACL.target_name("pyshacloid") is None


@pytest.mark.parametrize(
    "environ",
    [
        {"PYSHACL_TURBO_ALIAS": "0"},
        {"PYSHACL_TURBO_ALIAS": " Off "},
        {"PYSHACL_TURBO_ALIAS": "false"},
        {"TURBO_ALIAS": "no"},
        {"PYSHACL_TURBO_ALIAS": "1", "TURBO_ALIAS": "0"},
    ],
)
def test_either_switch_turns_the_alias_off(environ):
    assert not PYSHACL.enabled(environ)
    assert AliasFinder(PYSHACL, environ).find_spec("pyshacl") is None


@pytest.mark.parametrize("environ", [{}, {"PYSHACL_TURBO_ALIAS": "1"}, {"TURBO_ALIAS": "yes"}])
def test_the_alias_is_on_by_default(environ):
    assert PYSHACL.enabled(environ)


def test_the_finder_binds_the_alias_to_the_compatibility_module():
    finder = AliasFinder(PYSHACL, {})
    assert finder.find_spec("rdflib") is None
    package = finder.find_spec("pyshacl")
    assert package.name == "pyshacl" and package.submodule_search_locations is not None
    assert package.loader.create_module(package) is compat
    assert package.loader.exec_module(compat) is None
    errors = finder.find_spec("pyshacl.errors")
    assert errors.submodule_search_locations is None
    assert errors.loader.create_module(errors) is importlib.import_module(
        "pyshacl_turbo.compat.errors"
    )
    assert isinstance(finder.find_spec("pyshacl.rdfutil").loader, AliasLoader)
    assert finder.find_spec("pyshacl.rdfutil").submodule_search_locations is not None


def test_a_module_the_compatibility_package_lacks_is_a_typed_error():
    with pytest.raises(TurboAliasError) as error:
        AliasFinder(PYSHACL, {}).find_spec("pyshacl.sh_http")
    message = str(error.value)
    assert error.value.name == "pyshacl.sh_http" and isinstance(error.value, ImportError)
    assert "pyshacl-turbo" in message and "real pyshacl distribution" in message
    assert "PYSHACL_TURBO_ALIAS=0" in message and "TURBO_ALIAS=0" in message


def test_module_execution_uses_the_compatibility_code():
    code = AliasLoader("pyshacl_turbo.compat.__main__").get_code("pyshacl.__main__")
    assert code.co_filename.endswith(os.path.join("compat", "__main__.py"))


def test_install_registers_one_finder_first():
    finders = [object()]
    finder = hook.install(finders)
    assert finders[0] is finder and finder.alias is PYSHACL
    assert hook.install(finders) is finder and len(finders) == 2
    # The interpreter's own .pth already installed the alias in this process.
    assert hook.install() in sys.meta_path
    assert sum(isinstance(f, AliasFinder) for f in sys.meta_path) == 1


def test_turbo_alias_reports_the_owning_distribution():
    alias = TurboAlias(
        name="owlrl",
        target="owlrl_turbo.compat",
        distribution="owlrl-turbo",
        switch="OWLRL_TURBO_ALIAS",
    )
    assert alias.target_name("owlrl.x") == "owlrl_turbo.compat.x"
    assert "owlrl-turbo" in str(TurboAliasError(alias, "owlrl.x"))


def test_import_pyshacl_is_turbo_by_default_with_the_reference_installed():
    code = (
        "import sys, pyshacl, pyshacl_turbo; from pyshacl.errors import ConstraintLoadError; "
        "from pyshacl.rdfutil import load_from_source; import pyshacl.validator_conformance; "
        "print(pyshacl.__turbo__, pyshacl.__version__, pyshacl.validate is pyshacl_turbo.validate, "
        "ConstraintLoadError is pyshacl_turbo.ConstraintLoadError, "
        "sys.modules['pyshacl'] is sys.modules['pyshacl_turbo.compat'])"
    )
    assert python(code, alias_env())[:2] == (0, "True 0.40.2 True True True")


@pytest.mark.parametrize("switch", ["PYSHACL_TURBO_ALIAS", "TURBO_ALIAS"])
def test_turning_the_alias_off_imports_the_reference(switch):
    code = (
        "import pyshacl, pyshacl.errors; "
        "print(hasattr(pyshacl, '__turbo__'), pyshacl.__version__, "
        "pyshacl.errors.__name__, pyshacl.__name__)"
    )
    status, out, _ = python(code, alias_env(**{switch: "0"}))
    assert (status, out) == (0, "False 0.40.2 pyshacl.errors pyshacl")


def test_the_startup_hook_loads_no_engine_code():
    code = "import sys; print('pyshacl_turbo_alias' in sys.modules, 'rdflib' in sys.modules)"
    assert python(code, alias_env())[:2] == (0, "True False")


def test_an_unprovided_module_names_both_distributions_in_a_child():
    status, _, err = python("import pyshacl.sh_http", alias_env())
    assert status == 1 and "TurboAliasError" in err and "PYSHACL_TURBO_ALIAS=0" in err


def test_the_compatibility_package_marks_itself():
    assert compat.__turbo__ is True
    assert compat.__turbo_version__ == pyshacl_turbo.__version__
    assert compat.__version__ == compat.PYSHACL_API_VERSION == "0.40.2"


@pytest.mark.parametrize(
    ("command", "module", "target"),
    [
        (hook.validate_command, "pyshacl.cli", "main"),
        (hook.rules_command, "pyshacl.cli_rules", "main"),
    ],
)
def test_console_commands_follow_the_switch(monkeypatch, command, module, target):
    calls = []

    class Command:
        @staticmethod
        def main():
            calls.append(module)

    monkeypatch.setattr(hook.importlib, "import_module", lambda name: Command)
    command()
    assert calls == [module]


@pytest.mark.parametrize("name", ["pyshacl", "pyshacl.cli"])
def test_console_commands_explain_a_missing_reference(monkeypatch, name):
    def missing(_):
        raise ModuleNotFoundError(f"No module named {name!r}", name=name)

    monkeypatch.setattr(hook.importlib, "import_module", missing)
    with pytest.raises(SystemExit, match="PYSHACL_TURBO_ALIAS=0 selects the real pyshacl"):
        hook.validate_command()


def test_console_commands_keep_unrelated_import_errors(monkeypatch):
    def missing(_):
        raise ModuleNotFoundError("No module named 'rdflib'", name="rdflib")

    monkeypatch.setattr(hook.importlib, "import_module", missing)
    with pytest.raises(ModuleNotFoundError, match="rdflib"):
        hook.rules_command()


def test_console_commands_run_the_reference_when_the_alias_is_off(tmp_path):
    script = Path(sys.executable).parent / ("pyshacl.exe" if sys.platform == "win32" else "pyshacl")
    for alias, expected in (("1", "pyshacl_turbo"), ("0", "PySHACL Version: 0.40.2")):
        with Popen(
            [str(script), "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=alias_env(PYSHACL_TURBO_ALIAS=alias),
        ) as process:
            out, err = process.communicate(timeout=120)
        assert process.returncode == 0
        text = out + err
        if alias == "1":
            assert text.strip() == pyshacl_turbo.__version__
        else:
            assert expected in text


@pytest.mark.parametrize("module", ["pyshacl_turbo.compat.cli", "pyshacl_turbo.compat.cli_rules"])
def test_compat_commands_exit_with_the_command_status(monkeypatch, tmp_path, module, capsys):
    monkeypatch.setattr(sys, "argv", ["pyshacl", str(tmp_path / "missing.ttl")])
    with pytest.raises(SystemExit) as status:
        importlib.import_module(module).main()
    assert status.value.code == 1
    with pytest.raises(SystemExit):
        runpy.run_module(module, run_name="__main__")
    monkeypatch.setattr(sys, "argv", ["pyshacl", "--version"])
    with pytest.raises(SystemExit) as status:
        runpy.run_module("pyshacl_turbo.compat", run_name="__main__")
    assert status.value.code == 0

"""Published companions execute together before any native instrumentation."""

import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from rdflib import Namespace
from rdflib.namespace import RDF


def helper():
    path = Path(__file__).resolve().parents[1] / "scripts/provider_validation.py"
    spec = importlib.util.spec_from_file_location("provider_validation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def runtime(tmp_path, monkeypatch, defect):
    owner = tmp_path / "owner"
    (owner / "scripts").mkdir(parents=True)
    (owner / "scripts/pure_companion.py").write_text(
        "def verify_loaded(wheel, environment):\n"
        "    return {'payload': {'owlrl_turbo/__init__.py': 'original'}, "
        "'wheel_sha256': 'original'}\n"
    )
    (owner / "scripts/yaml_test_inputs.py").write_text(
        "calls = 0\n"
        "def verify_loaded(wheel, environment):\n"
        "    global calls\n    calls += 1\n"
        + (
            "    raise ValueError('YAML payload rejected before pipeline')\n"
            if defect == "yaml-missing"
            else "    return {'wheel_sha256': 'yaml-original', 'origin': str(environment), "
            "'payload': {'yaml/__init__.py': "
            + ("'changed' if calls > 1 else 'original'" if defect == "yaml-drift" else "'original'")
            + "}, 'loaded_modules': {}}\n"
        )
    )
    ex = Namespace("urn:published-companion-check:")

    class Dataset:
        def __init__(self):
            self.store = SimpleNamespace(backend=SimpleNamespace(_native=object()))
            self.rows = set()

        def add(self, triple):
            self.rows.add(triple)

        def __contains__(self, triple):
            return triple in self.rows

    class DeductiveClosure:
        def __init__(self, semantics):
            assert semantics == "actual-semantics"

        def expand(self, data):
            if defect != "missing-consequence":
                data.add((ex.subject, RDF.type, ex.Parent))
            if defect == "closure-owner":
                data.store.backend._native = object()

    def validate(data, *, shacl_graph):
        assert shacl_graph
        if defect == "validation-owner":
            data.store.backend._native = object()
        return defect != "nonconforming", None, "control"

    native = ModuleType("rdflib_turbo")
    native.Dataset = Dataset
    native.StoreDataset = object() if defect == "legacy-dataset" else Dataset
    owl = ModuleType("owlrl_turbo")
    if defect != "missing-api":
        owl.DeductiveClosure = DeductiveClosure
        owl.RDFS_OWLRL_Semantics = "actual-semantics"
    facade = ModuleType("pyshacl_turbo")
    facade.validate = validate
    for module in (native, owl, facade):
        monkeypatch.setitem(sys.modules, module.__name__, module)
    return (
        owner,
        tmp_path / "original-owl.whl",
        tmp_path / "project",
        tmp_path / "original-yaml.whl",
    )


def invoke(args, tmp_path):
    script = tmp_path / "installed-pipeline-probe.py"
    script.write_text(helper().owl_probe(*args))
    runpy.run_path(str(script), run_name="__main__")


def test_actual_companion_probe_executes_closure_and_validation_on_one_owner(
    tmp_path, monkeypatch, capsys
):
    args = runtime(tmp_path, monkeypatch, None)
    invoke(args, tmp_path)
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["pipeline"] == {
        "canonical_dataset": True,
        "inferred_type": True,
        "conforms": True,
        "same_native_owner": True,
    }
    assert receipt["installed"]["payload"] == {"owlrl_turbo/__init__.py": "original"}
    assert receipt["yaml_installed"]["payload"] == {"yaml/__init__.py": "original"}


@pytest.mark.parametrize(
    "defect",
    [
        "missing-api",
        "legacy-dataset",
        "missing-consequence",
        "closure-owner",
        "validation-owner",
        "nonconforming",
        "yaml-drift",
    ],
)
def test_imports_alone_or_changed_runtime_semantics_cannot_pass_the_gate(
    tmp_path, monkeypatch, defect
):
    args = runtime(tmp_path, monkeypatch, defect)
    with pytest.raises((ImportError, RuntimeError)):
        invoke(args, tmp_path)


def test_yaml_loaded_payload_is_verified_before_the_early_pipeline(tmp_path, monkeypatch):
    args = runtime(tmp_path, monkeypatch, "yaml-missing")
    with pytest.raises(ValueError, match="YAML payload rejected before pipeline"):
        invoke(args, tmp_path)


def test_post_gate_owl_payload_drift_is_not_hidden_by_unchanged_native_pair(tmp_path, monkeypatch):
    module = helper()
    native, facade = {"provider": "original"}, {"facade": "original"}
    context = {
        "owner": tmp_path / "owner",
        "wheel": tmp_path / "facade.whl",
        "project": tmp_path / "project",
        "environment": {},
        "receipt": {
            "provider": {
                "peers": {
                    "owlrl": {"wheel": str(tmp_path / "owl.whl")},
                    "yaml_test_dependency": {"authority": "yaml.json", "record": {}},
                }
            },
            "installed_provider": native,
            "installed_facade": facade,
            "installed_owlrl": {"installed": {"payload": "original"}},
            "installed_yaml": {"yaml": "original"},
        },
    }
    monkeypatch.setattr(module, "installed_receipts", lambda *args: (native, facade))
    monkeypatch.setattr(
        module,
        "load",
        lambda name: SimpleNamespace(
            verify_yaml_test_dependency=lambda *args: {"wheel": tmp_path / "yaml.whl"}
        ),
    )
    monkeypatch.setattr(module, "installed_yaml_receipt", lambda *args: {"yaml": "original"})
    monkeypatch.setattr(
        module,
        "installed_owl_receipt",
        lambda *args, **kwargs: {"installed": {"payload": "changed"}},
    )
    with pytest.raises(ValueError, match="Installed OWL runtime payload changed"):
        module.verify_runtime(context)

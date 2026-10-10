"""An upstream case keeps its identity when the checkout moves machines."""

import importlib.util
from pathlib import Path

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

import ntpath
import nturl2path
from pathlib import Path, PureWindowsPath

import pytest
import suite_harness
from rdflib import RDF, BNode, Graph, Literal
from rdflib.compare import isomorphic
from suite_harness import SH, cases, report_view
from test_compatibility import EX, graph


@pytest.mark.parametrize("name", ["space file.ttl", "unicode-Ω.ttl", "literal%20.ttl"])
def test_local_file_uri_decodes_exactly_once_inside_pinned_tree(tmp_path, monkeypatch, name):
    root = tmp_path / "pinned"
    root.mkdir()
    target = root / name
    target.write_text("fixture")
    monkeypatch.setattr(suite_harness, "ROOT", root)
    assert suite_harness.local_path(target.as_uri()) == target.resolve()


def test_local_file_uri_rejects_external_paths_and_authorities(tmp_path, monkeypatch):
    root = tmp_path / "pinned"
    root.mkdir()
    monkeypatch.setattr(suite_harness, "ROOT", root)
    for uri in ((tmp_path / "outside.ttl").as_uri(), "file://remote/fixture.ttl", "https://x/a"):
        with pytest.raises(ValueError):
            suite_harness.local_path(uri)


def test_local_file_uri_rejects_symlink_escape(tmp_path, monkeypatch):
    root, outside = tmp_path / "pinned", tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (outside / "fixture.ttl").write_text("fixture")
    (root / "escape").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(suite_harness, "ROOT", root)
    with pytest.raises(ValueError, match="escapes pinned tree"):
        suite_harness.local_path((root / "escape/fixture.ttl").as_uri())


def test_windows_drive_file_uri_uses_windows_path_decoding(monkeypatch):
    class WindowsPath(PureWindowsPath):
        def resolve(self):
            # Lexical Windows semantics only; actual filesystem acceptance is CI.
            return WindowsPath(ntpath.normpath(str(self)))

    root = WindowsPath("D:/suite root/w3c")
    target = root / "unicode-Ω%20.ttl"
    monkeypatch.setattr(suite_harness, "ROOT", root)
    monkeypatch.setattr(suite_harness, "Path", WindowsPath)
    monkeypatch.setattr(suite_harness, "url2pathname", nturl2path.url2pathname, raising=False)
    assert suite_harness.local_path(target.as_uri()) == target
    with pytest.raises(ValueError, match="escapes pinned tree"):
        suite_harness.local_path("file:///E:/outside.ttl")


def view(report):
    root = report.value(predicate=RDF.type, object=SH.ValidationReport)
    return report_view(report, root, messages=False, details=False)


def test_equivalent_shared_and_copied_paths_compare_equal():
    shared = graph("""[] a sh:ValidationReport; sh:conforms false;
        sh:result [sh:focusNode ex:a; sh:resultPath _:p], [sh:focusNode ex:b; sh:resultPath _:p].
        _:p sh:inversePath ex:p.""")
    copied = graph("""[] a sh:ValidationReport; sh:conforms false;
        sh:result [sh:focusNode ex:a; sh:resultPath [sh:inversePath ex:p]],
                  [sh:focusNode ex:b; sh:resultPath [sh:inversePath ex:p]].""")
    assert isomorphic(view(shared), view(copied))


@pytest.mark.parametrize(
    "field,value",
    [
        (SH.resultPath, EX.q),
        (SH.focusNode, EX.b),
        (SH.value, Literal(42)),
        (SH.resultSeverity, SH.Warning),
        (SH.sourceShape, EX.Other),
        (SH.sourceConstraintComponent, SH.ClassConstraintComponent),
    ],
)
@pytest.mark.parametrize("documents", [False, True])
def test_comparator_rejects_changed_report_fields(field, value, documents):
    original = graph("""[] a sh:ValidationReport; sh:conforms false;
        sh:result [sh:focusNode ex:a; sh:resultPath ex:p; sh:sourceShape ex:S;
            sh:resultSeverity sh:Violation; sh:sourceConstraintComponent sh:InConstraintComponent;
            sh:value 1].""")
    changed = Graph() + original
    node = changed.value(predicate=SH.focusNode, object=EX.a)
    changed.set((node, field, value))
    projection = document_view if documents else view
    assert not isomorphic(projection(original), projection(changed))


def test_comparator_rejects_dropped_or_duplicate_result():
    original = graph("[] a sh:ValidationReport; sh:conforms false; sh:result [sh:focusNode ex:a].")
    changed = Graph() + original
    root = changed.value(predicate=RDF.type, object=SH.ValidationReport)
    changed.add((root, SH.result, BNode("extra")))
    changed.add((BNode("extra"), SH.focusNode, EX.a))
    assert not isomorphic(view(original), view(changed))


def document_view(report):
    root = report.value(predicate=RDF.type, object=SH.ValidationReport)
    return report_view(report, root, messages=False, details=False, preserve_input_ids=False)


def test_document_comparator_matches_anonymous_shapes_by_description():
    text = """[] a sh:ValidationReport; sh:conforms false;
        sh:result [sh:focusNode ex:a; sh:sourceShape _:shape].
        _:shape sh:path ex:p; sh:minCount 1."""
    first, second = graph(text), graph(text)
    assert not isomorphic(view(first), view(second))
    assert isomorphic(document_view(first), document_view(second))
    shape = second.value(predicate=SH.path, object=EX.p)
    second.set((shape, SH.minCount, Literal(2)))
    assert not isomorphic(document_view(first), document_view(second))


def test_document_comparator_retains_shared_blank_node_references():
    original = graph("""[] a sh:ValidationReport; sh:conforms false;
        sh:result [sh:focusNode _:node; sh:value _:node].
        _:node ex:p 1.""")
    changed = graph("""[] a sh:ValidationReport; sh:conforms false;
        sh:result [sh:focusNode _:node; sh:value _:other].
        _:node ex:p 1. _:other ex:p 1.""")
    assert not isomorphic(document_view(original), document_view(changed))


def test_document_comparator_rejects_missing_and_duplicate_results():
    original = graph("[] a sh:ValidationReport; sh:conforms false; sh:result [sh:focusNode ex:a].")
    changed = Graph() + original
    root = changed.value(predicate=RDF.type, object=SH.ValidationReport)
    result = changed.value(root, SH.result)
    changed.remove((root, SH.result, result))
    assert not isomorphic(document_view(original), document_view(changed))
    changed.add((root, SH.result, result))
    changed.add((root, SH.result, BNode("extra")))
    changed.add((BNode("extra"), SH.focusNode, EX.a))
    assert not isomorphic(document_view(original), document_view(changed))


@pytest.mark.parametrize("windows_paths", [False, True])
def test_inventory_retains_executed_upstream_failures(tmp_path, monkeypatch, windows_paths):
    import json
    import runpy
    import sys

    root = Path(__file__).resolve().parents[1]
    main = runpy.run_path(str(root / "scripts/coverage_inventory.py"))["main"]
    (tmp_path / "vendor/pyshacl/test").mkdir(parents=True)
    (tmp_path / "vendor/pyshacl/test/test_sample.py").write_text(
        "def test_sample(): pass\ndef test_unexecuted(): pass\n"
    )
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/suite-sources.json").write_text("{}")
    (tmp_path / "docs").mkdir()
    report = {
        "summary": {"passed": 1, "failed": 1},
        "cases": [
            {"id": "test/test_sample.py::test_sample[a]", "status": "passed"},
            {"id": "test/test_sample.py::test_sample[b]", "status": "failed"},
        ],
    }
    (tmp_path / "docs/upstream-coverage.json").write_text(json.dumps(report))
    output = tmp_path / "inventory.json"
    monkeypatch.setitem(main.__globals__, "ROOT", tmp_path)
    unique_lang = next(case for case in cases() if case.path.stem == "uniqueLang-002")
    monkeypatch.setitem(main.__globals__, "cases", lambda: [unique_lang])
    monkeypatch.setattr(sys, "argv", ["coverage_inventory.py", str(output)])
    if windows_paths:
        original = Path.relative_to

        def relative(path, *args, **kwargs):
            return PureWindowsPath(original(path, *args, **kwargs).as_posix())

        monkeypatch.setattr(Path, "relative_to", relative)
    main()
    result = json.loads(output.read_text())
    assert result["w3c_summary"] == {"mismatch": 1}
    assert result["w3c_document_summary"] == {"pass": 1}
    assert result["w3c"][0]["id"] == result["w3c_documents"][0]["id"]
    assert result["upstream_run"]["summary"] == report["summary"]
    statuses = {row["name"]: row["status"] for row in result["upstream"]}
    assert statuses == {"test_sample": "failed", "test_unexecuted": "not_run"}

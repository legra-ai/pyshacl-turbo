import pytest
from rdflib import RDF, BNode, Graph, Literal
from rdflib.compare import isomorphic
from suite_harness import SH, cases, report_view
from test_compatibility import EX, graph


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


def test_inventory_retains_executed_upstream_failures(tmp_path, monkeypatch):
    import json
    import runpy
    import sys
    from pathlib import Path

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
    main()
    result = json.loads(output.read_text())
    assert result["w3c_summary"] == {"mismatch": 1}
    assert result["w3c_document_summary"] == {"pass": 1}
    assert result["w3c"][0]["id"] == result["w3c_documents"][0]["id"]
    assert result["upstream_run"]["summary"] == report["summary"]
    statuses = {row["name"]: row["status"] for row in result["upstream"]}
    assert statuses == {"test_sample": "failed", "test_unexecuted": "not_run"}

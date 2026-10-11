import io
import logging
import runpy
import sys

import pytest
from pyshacl_turbo import cli
from pyshacl_turbo.cli import main
from rdflib import Dataset, Graph
from rdflib.namespace import SH
from test_compatibility import EX, PREFIXES


def test_rules_cli_trig_keeps_default_graph(tmp_path, capsys):
    data, shapes = tmp_path / "data.ttl", tmp_path / "shapes.ttl"
    data.write_text(PREFIXES + "ex:s ex:p 1.")
    shapes.write_text(
        PREFIXES
        + """ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule;
       sh:subject sh:this; sh:predicate ex:q; sh:object 2]."""
    )
    assert main(["--rules", str(data), "-s", str(shapes)]) == 0
    output = Graph().parse(data=capsys.readouterr().out, format="trig")
    assert (EX.s, EX.q, None) in output


@pytest.fixture
def cli_files(tmp_path):
    data, shapes = tmp_path / "data.ttl", tmp_path / "shapes.ttl"
    data.write_text(PREFIXES + 'ex:s ex:p "value".')
    shapes.write_text(PREFIXES + "ex:S sh:targetNode ex:s; sh:path ex:required; sh:minCount 1.")
    return data, shapes


@pytest.mark.parametrize("fmt", ["turtle", "trig", "xml", "json-ld", "nt", "n3", "nquads"])
def test_validation_cli_serializes_complete_reports(cli_files, capsys, fmt):
    data, shapes = cli_files
    assert main([str(data), "-s", str(shapes), "-f", fmt]) == 1
    output = capsys.readouterr()
    assert not output.err
    report = Dataset(default_union=True) if fmt in {"trig", "nquads"} else Graph()
    report.parse(data=output.out, format=fmt)
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert list(report.objects(None, SH.resultPath)) == [EX.required]


@pytest.mark.parametrize("conforming", [False, True])
def test_validation_cli_table(cli_files, capsys, conforming):
    data, shapes = cli_files
    args = [str(data), "-f", "table"]
    if not conforming:
        args += ["-s", str(shapes)]
    assert main(args) == (0 if conforming else 1)
    output = capsys.readouterr().out
    assert "Conforms" in output and str(conforming) in output
    assert ("MinCountConstraint" in output) is not conforming


def test_table_wraps_long_values_and_aligns_shorter_columns():
    output = cli.table(["a", "b"], [["x" * 26, "y"], ["", ""]])
    rows = output.splitlines()
    assert len(set(map(len, rows))) == 1
    assert rows[3] == "| " + "x" * 25 + " | y |"
    assert rows[4] == "| x" + " " * 24 + " |   |"
    assert cli.report_table(False, Graph()).count("False") == 1


def test_cli_reads_stdin_and_writes_output_file(cli_files, tmp_path, monkeypatch, capsys, caplog):
    data, shapes = cli_files
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(data.read_bytes())))
    output = tmp_path / "report.ttl"
    with caplog.at_level(logging.DEBUG, logger="pyshacl-turbo"):
        assert main(["-", "-s", str(shapes), "-f", "turtle", "-o", str(output), "--debug"]) == 1
    assert not capsys.readouterr().out
    report = Graph().parse(output, format="turtle")
    assert list(report.objects(None, SH.focusNode)) == [EX.s]
    assert "Validating with the native Rust engine" in caplog.text


def test_cli_combines_inputs_and_expands_focus_and_shape_names(cli_files, tmp_path, capsys):
    data, shapes = cli_files
    second = tmp_path / "second.ttl"
    second.write_text(PREFIXES + "ex:s ex:required 1.")
    assert (
        main([str(data), str(second), "-s", str(shapes), "--focus", "ex:s", "--shape", "ex:S"]) == 0
    )
    assert "Conforms: True" in capsys.readouterr().out


@pytest.mark.parametrize("fmt", ["human", "table", "turtle"])
def test_cli_preserves_validation_failure_text(cli_files, capsys, fmt):
    data, shapes = cli_files
    shapes.write_text(
        PREFIXES
        + 'ex:S sh:targetNode ex:s; sh:sparql [sh:select "SELECT $this WHERE { VALUES ?v { 1 } }"].'
    )
    assert main([str(data), "-s", str(shapes), "-f", fmt]) == 1
    assert "Validation Failure" in capsys.readouterr().out


@pytest.mark.parametrize("problem", ["missing-file", "invalid-shape", "js"])
def test_cli_errors_use_documented_exit_codes(cli_files, capsys, problem):
    data, shapes = cli_files
    args = [str(data), "-s", str(shapes)]
    if problem == "missing-file":
        args[0] += ".missing"
    elif problem == "invalid-shape":
        shapes.write_text(PREFIXES + "ex:S a sh:PropertyShape; sh:path 42.")
    else:
        args.append("--js")
    assert main(args) == (3 if problem == "js" else 2)
    output = capsys.readouterr()
    assert output.err and not output.out


@pytest.mark.parametrize("fmt", ["turtle", "nquads", "trig"])
def test_rules_cli_keeps_named_graphs(cli_files, capsys, fmt):
    data, shapes = cli_files
    data.write_text(PREFIXES + "ex:g { ex:s ex:p 1. }")
    shapes.write_text(
        PREFIXES
        + "ex:S sh:targetNode ex:s; sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:q; sh:object 2]."
    )
    assert main(["--rules", str(data), "-df", "trig", "-s", str(shapes), "-f", fmt]) == 0
    output = capsys.readouterr().out
    result = Dataset(default_union=True) if fmt in {"trig", "nquads"} else Graph()
    result.parse(data=output, format=fmt)
    assert (EX.s, EX.q, None) in result
    if fmt in {"trig", "nquads"}:
        assert (EX.s, EX.p, None) in result.graph(EX.g)


@pytest.mark.parametrize("entry", ["validate", "rules", "package", "module"])
def test_console_and_module_entrypoints(cli_files, monkeypatch, capsys, entry):
    data, _ = cli_files
    monkeypatch.setattr(sys, "argv", ["pyshacl-turbo", str(data)])
    with pytest.raises(SystemExit) as exited:
        if entry == "validate":
            cli.entrypoint()
        elif entry == "rules":
            cli.rules_entrypoint()
        elif entry == "package":
            runpy.run_module("pyshacl_turbo", run_name="__main__")
        else:
            with pytest.warns(RuntimeWarning, match="found in sys.modules"):
                runpy.run_module("pyshacl_turbo.cli", run_name="__main__")
    assert exited.value.code == 0
    assert capsys.readouterr().out

from pyshacl_turbo.cli import main
from rdflib import Graph
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

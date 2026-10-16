"""Function callbacks share only the immutable data phase they execute against."""

import pyshacl_turbo as turbo
from rdflib import Literal
from test_compatibility import EX, graph


def test_callbacks_read_current_rule_phase_and_current_invocation():
    shapes = graph("""
      ex:count a sh:SPARQLFunction;
        sh:select "SELECT (COUNT(?s) AS ?result) WHERE { ?s ex:marker true }".
      ex:S sh:targetSubjectsOf ex:p;
        sh:rule ex:Mark, ex:Count.
      ex:Mark a sh:SPARQLRule; sh:order 0;
        sh:construct "CONSTRUCT { $this ex:marker true } WHERE {}".
      ex:Count a sh:SPARQLRule; sh:order 1;
        sh:construct "CONSTRUCT { $this ex:count ?n } WHERE { BIND(ex:count() AS ?n) }".
    """)
    compiled = turbo.compile_shapes(shapes, advanced=True)
    for count in [12, 3]:
        data = graph(" ".join(f"ex:s{i} ex:p 1." for i in range(count)))
        result = compiled.shacl_rules(data)
        assert set(result.objects(None, EX["count"])) == {Literal(count)}
        assert len(list(result.triples((None, EX["count"], None)))) == count
        assert not list(data.triples((None, EX.marker, None)))

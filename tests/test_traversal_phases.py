"""Read caches expire whenever a rule commits changes to its data phase."""

import pyshacl_turbo as turbo
from rdflib import Literal
from test_compatibility import EX, graph


def test_rule_condition_path_and_class_caches_expire_after_additions():
    shapes = graph("""
      ex:Ready sh:class ex:Enabled;
        sh:property [sh:path [sh:oneOrMorePath ex:p]; sh:minCount 1].
      ex:S sh:targetNode ex:s; sh:rule ex:Before, ex:Enable, ex:After.
      ex:Before a sh:TripleRule; sh:order 0; sh:condition ex:Ready;
        sh:subject sh:this; sh:predicate ex:before; sh:object true.
      ex:Enable a sh:SPARQLRule; sh:order 1;
        sh:construct "CONSTRUCT { $this a ex:Enabled; ex:p 1 } WHERE {}".
      ex:After a sh:TripleRule; sh:order 2; sh:condition ex:Ready;
        sh:subject sh:this; sh:predicate ex:after; sh:object true.
    """)
    program = turbo.compile_shapes(shapes, advanced=True)
    for _ in range(2):
        data = graph("")
        result = program.shacl_rules(data)
        assert (EX.s, EX.before, None) not in result
        assert (EX.s, EX.after, Literal(True)) in result
        assert not data


def test_class_target_cache_expires_after_type_and_subclass_additions():
    program = turbo.compile_shapes(
        graph("""
          ex:Before sh:order 0; sh:targetClass ex:Base; sh:rule [a sh:TripleRule;
            sh:subject sh:this; sh:predicate ex:before; sh:object true].
          ex:Enable sh:order 1; sh:targetNode ex:s; sh:rule [a sh:SPARQLRule;
            sh:construct "CONSTRUCT { $this a ex:Child . ex:Child rdfs:subClassOf ex:Base } WHERE {}"].
          ex:After sh:order 2; sh:targetClass ex:Base; sh:rule [a sh:TripleRule;
            sh:subject sh:this; sh:predicate ex:after; sh:object true].
        """),
        advanced=True,
    )
    result = program.shacl_rules(graph(""))
    assert (EX.s, EX.before, None) not in result
    assert (EX.s, EX.after, Literal(True)) in result

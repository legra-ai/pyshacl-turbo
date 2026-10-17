use super::*;
use oxigraph::io::RdfFormat;

fn graph(body: &str) -> Dataset {
    crate::parse_graph(
        &format!(
            "@prefix sh: <http://www.w3.org/ns/shacl#>. @prefix ex: <https://example.org/>. {body}"
        ),
        RdfFormat::Turtle,
        None,
    )
    .unwrap()
}

#[test]
fn shape_declarations_fail_fast_for_inconsistent_roles_messages_and_paths() {
    let node = iri("https://example.org/", "S").into();
    for body in [
        "ex:S a sh:NodeShape; sh:path ex:p.",
        "ex:S a sh:PropertyShape.",
        "ex:S sh:message ex:notLiteral.",
        "ex:S sh:path ex:unresolved.",
        "ex:S sh:severity 'not an IRI'.",
    ] {
        assert!(
            read_shape(
                &graph(body),
                &node,
                &HashMap::new(),
                true,
                &Functions::default(),
                &[]
            )
            .is_err(),
            "{body}"
        );
    }
    assert!(iri_value(NamedNode::new_unchecked("invalid IRI").into(), "shape").is_err());
}

#[test]
fn validator_and_rule_readers_reject_incomplete_declarations() {
    let node = iri("https://example.org/", "node").into();
    let data = graph("");
    assert!(validator(&data, &node, true).is_err());
    assert!(validator(&data, &node, false).is_err());
    assert!(target_type(&data, &node).is_err());
    for body in [
        "ex:node a sh:SPARQLRule.",
        "ex:node a sh:TripleRule; sh:subject sh:this; sh:predicate ex:p.",
        "ex:node a sh:TripleRule; sh:subject sh:this; sh:object ex:o.",
        "ex:node a sh:TripleRule; sh:predicate ex:p; sh:object ex:o.",
        "ex:node a ex:UnknownRule.",
    ] {
        assert!(
            rule(&graph(body), &node, &Functions::default()).is_err(),
            "{body}"
        );
    }
}

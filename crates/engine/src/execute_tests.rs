use super::*;
use oxigraph::io::RdfFormat;

fn rules() -> CompiledShapes {
    CompiledShapes::compile(parse("@prefix sh: <http://www.w3.org/ns/shacl#>. <urn:S> sh:targetNode <urn:s>; sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate <urn:derived>; sh:object true].", RdfFormat::Turtle, None).unwrap(), true).unwrap()
}

#[test]
fn rust_store_validation_and_rule_apis_commit_only_when_requested() {
    let program = rules();
    for inplace in [false, true] {
        for validate in [false, true] {
            let store = oxigraph::store::Store::new().unwrap();
            store
                .insert(QuadRef::new(
                    NamedNodeRef::new_unchecked("urn:s"),
                    NamedNodeRef::new_unchecked("urn:p"),
                    LiteralRef::new_simple_literal("plain"),
                    GraphNameRef::DefaultGraph,
                ))
                .unwrap();
            if validate {
                let report = program
                    .validate_store(&store, Options::default(), inplace)
                    .unwrap();
                assert!(report.conforms);
            } else {
                let expansion = program
                    .expand_store(&store, Options::default(), inplace)
                    .unwrap();
                assert_eq!(expansion.graph.len(), 2);
                assert!(expansion.recursion_warnings.is_empty());
            }
            assert_eq!(store.len().unwrap(), if inplace { 2 } else { 1 });
            let snapshot = store_snapshot(&store).unwrap();
            assert!(snapshot.iter().any(|q| matches!(q.object, TermRef::Literal(l) if l.value()=="plain" && l.has_explicit_datatype())));
        }
    }
}

#[test]
fn membership_traversal_handles_cycles_literals_and_missing_classes() {
    let data = parse("<urn:s> a <urn:A>. <urn:A> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:B>. <urn:B> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:A>.", RdfFormat::Turtle, None).unwrap();
    let node: Term = iri("urn:", "s").into();
    assert!(is_instance(&data, &node, &iri("urn:", "B").into()).unwrap());
    assert!(!is_instance(&data, &node, &iri("urn:", "absent").into()).unwrap());
    assert!(!is_instance(&data, &Literal::from(1).into(), &iri("urn:", "A").into()).unwrap());
    assert!(
        rules()
            .shape_focus_nodes("<urn:missing>", &data, true)
            .unwrap_err()
            .to_string()
            .contains("Unknown shape")
    );
    let options = Options::default();
    assert_eq!(options.clone().max_validation_depth, 15);
    assert!(format!("{options:?}").contains("max_rule_iterations"));
}

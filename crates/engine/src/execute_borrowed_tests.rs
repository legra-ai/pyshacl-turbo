use super::*;
use oxigraph::io::RdfFormat;
use oxigraph::store::Store;

#[test]
fn readonly_validation_uses_pending_named_graph_changes_and_borrowed_shapes_overlay() {
    let shapes = parse(r#"@prefix sh: <http://www.w3.org/ns/shacl#> .
        <urn:has> a sh:SPARQLFunction; sh:ask "ASK { <urn:s> <urn:p> ?value }" .
        <urn:S> sh:targetNode <urn:s>;
          sh:property [sh:path <urn:p>; sh:minCount 1];
          sh:sparql [sh:select "SELECT $this WHERE { GRAPH $shapesGraph { $currentShape <http://www.w3.org/ns/shacl#targetNode> $this } FILTER(!<urn:has>()) }"] ."#, RdfFormat::Turtle, None).unwrap();
    let program = CompiledShapes::compile(shapes, true).unwrap();
    let store = Store::new().unwrap();
    let mut transaction = store.start_transaction().unwrap();
    let quad = Quad::new(
        NamedNode::new_unchecked("urn:s"),
        NamedNode::new_unchecked("urn:p"),
        Literal::from(true),
        NamedNode::new_unchecked("urn:g"),
    );
    transaction.insert(quad.as_ref());
    assert!(
        program
            .validate_readonly(&transaction, Options::default())
            .unwrap()
            .conforms
    );
    transaction.remove(quad.as_ref());
    let report = program
        .validate_readonly(&transaction, Options::default())
        .unwrap();
    assert!(!report.conforms);
    assert!(report.text.contains("MinCountConstraintComponent"));
    assert!(report.text.contains("SPARQLConstraintComponent"));
    drop(transaction);
    assert_eq!(store.len().unwrap(), 0);
}

#[test]
fn rule_validation_stages_additions_in_the_callers_transaction_until_commit() {
    let shapes = parse(r#"@prefix sh: <http://www.w3.org/ns/shacl#> .
      <urn:S> sh:targetNode <urn:s>;
        sh:rule [a sh:SPARQLRule; sh:construct "CONSTRUCT { $this <urn:derived> ?value } WHERE { $this <urn:p> ?value }"];
        sh:property [sh:path <urn:derived>; sh:hasValue true]."#, RdfFormat::Turtle, None).unwrap();
    let program = CompiledShapes::compile(shapes, true).unwrap();
    for commit in [false, true] {
        let store = Store::new().unwrap();
        let mut transaction = store.start_transaction().unwrap();
        let source = Quad::new(
            NamedNode::new_unchecked("urn:s"),
            NamedNode::new_unchecked("urn:p"),
            Literal::from(true),
            NamedNode::new_unchecked("urn:g"),
        );
        let derived = Quad::new(
            NamedNode::new_unchecked("urn:s"),
            NamedNode::new_unchecked("urn:derived"),
            Literal::from(true),
            GraphName::DefaultGraph,
        );
        transaction.insert(source.as_ref());
        assert!(
            program
                .validate_transaction(&mut transaction, Options::default())
                .unwrap()
                .conforms
        );
        assert!(transaction.contains(derived.as_ref()).unwrap());
        assert_eq!(store.len().unwrap(), 0);
        if commit {
            transaction.commit().unwrap();
        } else {
            drop(transaction);
        }
        assert_eq!(store.len().unwrap(), if commit { 2 } else { 0 });
    }
}

#[test]
fn staged_validation_retains_only_rule_additions_and_does_not_change_pending_input() {
    let shapes = parse(
        r#"@prefix sh: <http://www.w3.org/ns/shacl#> .
      <urn:S> sh:targetNode <urn:s>;
        sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate <urn:derived>; sh:object true];
        sh:property [sh:path <urn:derived>; sh:hasValue true]."#,
        RdfFormat::Turtle,
        None,
    )
    .unwrap();
    let program = CompiledShapes::compile(shapes, true).unwrap();
    let store = Store::new().unwrap();
    let mut transaction = store.start_transaction().unwrap();
    let source = Quad::new(
        NamedNode::new_unchecked("urn:s"),
        NamedNode::new_unchecked("urn:p"),
        Literal::from(true),
        GraphName::DefaultGraph,
    );
    let derived = Quad::new(
        NamedNode::new_unchecked("urn:s"),
        NamedNode::new_unchecked("urn:derived"),
        Literal::from(true),
        GraphName::DefaultGraph,
    );
    transaction.insert(source.as_ref());
    assert!(
        program
            .validate_staged(&transaction, Options::default())
            .unwrap()
            .conforms
    );
    assert!(transaction.contains(source.as_ref()).unwrap());
    assert!(!transaction.contains(derived.as_ref()).unwrap());
    assert_eq!(store.len().unwrap(), 0);
}

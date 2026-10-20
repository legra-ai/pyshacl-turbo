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

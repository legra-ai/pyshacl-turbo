use super::*;

fn render(literal: Literal) -> String {
    let graph = Dataset::new();
    let namespaces = vec![
        ("xsd".into(), XSD.into()),
        ("ex".into(), "urn:example:".into()),
    ];
    let display = Display {
        shape_namespaces: namespaces.clone(),
        data_namespaces: namespaces,
        data: &graph,
        shapes: &graph,
    };
    display.term(&literal.into(), false).unwrap()
}

#[test]
fn report_literals_match_pinned_reference_lexical_identity() {
    let cases = [
        (Literal::new_simple_literal("plain"), "Literal(\"plain\")"),
        (
            Literal::new_simple_literal("say \"hi\"\\end"),
            "Literal(\"say \"hi\"\\end\")",
        ),
        (
            Literal::new_simple_literal("line\nnext\tcol\rreturn"),
            "Literal(\"line\nnext\tcol\rreturn\")",
        ),
        (
            Literal::new_language_tagged_literal("français", "fr").unwrap(),
            "Literal(\"français\", lang=fr)",
        ),
        (
            Literal::new_typed_literal("same", iri(XSD, "string")),
            "Literal(\"same\", datatype=xsd:string)",
        ),
        (
            Literal::new_typed_literal("1", iri(XSD, "integer")),
            "Literal(\"1\", datatype=xsd:integer)",
        ),
        (
            Literal::new_typed_literal("+001", iri(XSD, "integer")),
            "Literal(\"+001\" = 1, datatype=xsd:integer)",
        ),
        (
            Literal::new_typed_literal("true", iri(XSD, "boolean")),
            "Literal(\"true\" = True, datatype=xsd:boolean)",
        ),
        (
            Literal::new_typed_literal("1", iri(XSD, "boolean")),
            "Literal(\"1\" = True, datatype=xsd:boolean)",
        ),
        (
            Literal::new_typed_literal("01.20", iri(XSD, "decimal")),
            "Literal(\"01.20\" = 1.20, datatype=xsd:decimal)",
        ),
        (
            Literal::new_typed_literal("opaque", iri("urn:example:", "opaque")),
            "Literal(\"opaque\", datatype=ex:opaque)",
        ),
        (
            Literal::new_typed_literal("bad", iri(XSD, "integer")),
            "Literal(\"bad\", datatype=xsd:integer)",
        ),
    ];
    for (literal, expected) in cases {
        assert_eq!(render(literal.clone()), expected, "{literal}");
    }
}

#[test]
fn collection_descriptions_keep_order_exact_terms_and_selected_context() {
    let graph = parse_dataset(
        "@prefix ex:<urn:example:>. @prefix rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>. \
         @prefix xsd:<http://www.w3.org/2001/XMLSchema#>. \
         ex:g { _:head rdf:first \"z\"; rdf:rest _:tail. \
         _:tail rdf:first _:inner; rdf:rest rdf:nil. \
         _:inner rdf:first \"same\"^^xsd:string; rdf:rest _:last. \
         _:last rdf:first \"français\"@fr; rdf:rest rdf:nil. } \
         ex:other { _:head rdf:first \"WRONG\";rdf:rest rdf:nil. } \
         ex:aaa { _:inner rdf:first \"WRONG\";rdf:rest rdf:nil. }",
        oxigraph::io::RdfFormat::TriG,
        None,
    )
    .unwrap();
    let namespaces = vec![
        ("ex".into(), "urn:example:".into()),
        ("xsd".into(), XSD.into()),
        ("rdf".into(), RDF.into()),
    ];
    let display = Display {
        shape_namespaces: namespaces.clone(),
        data_namespaces: namespaces,
        data: &graph,
        shapes: &graph,
    };
    let head: Term = BlankNode::new("head").unwrap().into();
    assert_eq!(
        display.term(&head, false).unwrap(),
        "( Literal(\"z\") ( Literal(\"same\", datatype=xsd:string) Literal(\"français\", lang=fr) ) )"
    );
}

#[test]
fn malformed_and_cyclic_collection_descriptions_fail_before_partial_output() {
    for source in [
        "_:head <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <urn:p>.",
        "_:head <http://www.w3.org/1999/02/22-rdf-syntax-ns#first> <urn:p>; <http://www.w3.org/1999/02/22-rdf-syntax-ns#rest> _:head.",
    ] {
        let graph = parse(source, oxigraph::io::RdfFormat::Turtle, None).unwrap();
        let display = Display {
            shape_namespaces: Vec::new(),
            data_namespaces: Vec::new(),
            data: &graph,
            shapes: &graph,
        };
        let head: Term = BlankNode::new("head").unwrap().into();
        assert!(display.term(&head, false).is_err(), "{source}");
    }
}

#[test]
fn collection_descriptions_reject_deep_blank_items_instead_of_truncating() {
    let mut graph = Dataset::new();
    let head: Term = BlankNode::new("head").unwrap().into();
    // bounded: fixed 23-node regression fixture exceeds the display depth limit.
    let nodes: Vec<Term> = (0..23)
        .map(|index| BlankNode::new(format!("b{index}")).unwrap().into())
        .collect();
    add(&mut graph, &head, iri(RDF, "first"), nodes[0].clone()).unwrap();
    add(&mut graph, &head, iri(RDF, "rest"), iri(RDF, "nil").into()).unwrap();
    for pair in nodes.windows(2) {
        add(&mut graph, &pair[0], iri("urn:", "next"), pair[1].clone()).unwrap();
    }
    let display = Display {
        shape_namespaces: Vec::new(),
        data_namespaces: Vec::new(),
        data: &graph,
        shapes: &graph,
    };
    assert!(display.term(&head, false).is_err());
}

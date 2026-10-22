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

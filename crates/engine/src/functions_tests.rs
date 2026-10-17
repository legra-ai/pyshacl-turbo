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
fn function_declarations_reject_missing_ambiguous_and_mismatched_queries() {
    for body in [
        "ex:f a sh:SPARQLFunction.",
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {}'; sh:ask 'ASK {}'.",
        "ex:f a sh:SPARQLFunction; sh:select 'INVALID'.",
        "ex:f a sh:SPARQLFunction; sh:select 'ASK {}'.",
        "ex:f a sh:SPARQLFunction; sh:ask 'SELECT ?x WHERE {}'.",
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT * WHERE {}'.",
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {}'; sh:parameter [].",
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {}'; sh:parameter [sh:path <https://example.org/bad-name>].",
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {}'; sh:parameter [sh:path ex:x; sh:order ex:nonNumeric].",
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {}'; sh:parameter [sh:path ex:x; sh:order 'invalid'].",
    ] {
        assert!(Functions::compile(&graph(body), &[]).is_err(), "{body}");
    }
}

#[test]
fn optional_arguments_and_empty_function_results_have_explicit_semantics() {
    let data = graph(
        "ex:f a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {}'; sh:parameter [sh:path ex:x; sh:optional true]. ex:ask a sh:SPARQLFunction; sh:ask 'ASK {?s ?p ?o}'. ex:empty a sh:SPARQLFunction; sh:select 'SELECT ?x WHERE {FILTER(false)}'.",
    );
    let functions = Functions::compile(&data, &[]).unwrap();
    let f = iri("https://example.org/", "f");
    assert_eq!(functions.call(&f, &[], &data).unwrap(), None);
    assert_eq!(
        functions
            .call(&f, &[Literal::from(2).into()], &data)
            .unwrap(),
        Some(Literal::from(2).into())
    );
    assert!(
        functions
            .call(
                &f,
                &[Literal::from(1).into(), Literal::from(2).into()],
                &data
            )
            .is_err()
    );
    assert_eq!(
        functions
            .call(&iri("https://example.org/", "empty"), &[], &data)
            .unwrap(),
        None
    );
    assert_eq!(
        functions
            .call(&iri("https://example.org/", "ask"), &[], &data)
            .unwrap(),
        Some(Literal::from(true).into())
    );
    assert!(functions.call(&iri("urn:", "unknown"), &[], &data).is_err());
    assert!(
        functions
            .call_inner(&f, &[], Arc::new(data), 64)
            .unwrap_err()
            .to_string()
            .contains("recursion limit")
    );
}

#[test]
fn checked_iterators_deliver_pending_errors_once_and_remain_exhausted() {
    let mut checked = Checked {
        inner: vec![Ok(1), Ok(2)].into_iter(),
        errors: Arc::new(Mutex::new(Some(Error::Invalid("callback failed".into())))),
        done: false,
    };
    assert!(
        checked
            .next()
            .unwrap()
            .unwrap_err()
            .to_string()
            .contains("callback failed")
    );
    assert!(checked.next().is_none());
    assert!(checked.next().is_none());
    let mut checked = Checked {
        inner: vec![Ok(1)].into_iter(),
        errors: Arc::new(Mutex::new(None)),
        done: false,
    };
    assert_eq!(checked.next().unwrap().unwrap(), 1);
    assert!(checked.next().is_none());
    assert!(checked.next().is_none());
}

#[test]
fn regex_backed_graph_queries_use_checked_triple_results() {
    let data = Dataset::new();
    let QueryResults::Graph(triples) = evaluate_query(
        &data,
        &data,
        "CONSTRUCT { <urn:s> <urn:p> ?v } WHERE { BIND(REPLACE('abc', '(a)', '$1x') AS ?v) }",
        &[],
    )
    .unwrap() else {
        panic!("CONSTRUCT result expected")
    };
    let triples = triples.collect::<std::result::Result<Vec<_>, _>>().unwrap();
    assert_eq!(triples.len(), 1);
    assert_eq!(
        triples[0].object,
        Literal::new_simple_literal("axbc").into()
    );
    let prepared = NativePrepared {
        query: SparqlEvaluator::new().parse_query("ASK {}").unwrap(),
        errors: Some(Arc::new(Mutex::new(Some(Error::Invalid(
            "already failed".into(),
        ))))),
    };
    assert!(
        prepared
            .on_queryable_dataset(&data)
            .execute()
            .err()
            .unwrap()
            .to_string()
            .contains("already failed")
    );
}

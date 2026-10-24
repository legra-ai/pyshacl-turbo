use super::*;
use shacl_structural_model::{Component as C, ShaclPath};

#[test]
fn lowerer_rejects_unresolved_shape_references_and_non_predicate_pairs() {
    let data = Dataset::new();
    let node: Term = iri("urn:", "node").into();
    let missing: Term = iri("urn:", "missing").into();
    for component in [
        C::Node(missing.clone()),
        C::Not(missing.clone()),
        C::And(vec![missing.clone()]),
        C::Or(vec![missing.clone()]),
        C::Xone(vec![missing.clone()]),
        C::QualifiedValueShape {
            shape: missing,
            min_count: None,
            max_count: None,
            disjoint: false,
        },
    ] {
        assert!(
            lower_one(&data, &node, true, &HashMap::new(), component)
                .err()
                .unwrap()
                .to_string()
                .contains("Unknown shape")
        );
    }
    let path = ShaclPath::Predicate(iri_rfc3987::Iri::known("urn:p"));
    assert!(
        lower_one(
            &data,
            &node,
            false,
            &HashMap::new(),
            C::LessThan(path.clone())
        )
        .is_err()
    );
    assert!(
        lower_one(
            &data,
            &node,
            true,
            &HashMap::new(),
            C::Equals(ShaclPath::Inverse(Box::new(path)))
        )
        .is_err()
    );
    assert!(
        lower_one(&data, &node, true, &HashMap::new(), C::UniqueLang(false))
            .unwrap()
            .is_none()
    );
    assert!(
        lower_one(
            &data,
            &node,
            true,
            &HashMap::new(),
            C::Closed {
                is_closed: false,
                ignored_properties: vec![]
            }
        )
        .unwrap()
        .is_none()
    );
    assert!(
        lower_one(
            &data,
            &node,
            true,
            &HashMap::new(),
            C::Pattern {
                pattern: Literal::new_simple_literal("a").into(),
                flags: Some(node.clone())
            }
        )
        .is_err()
    );
}

#[test]
fn qualified_boolean_counts_keep_python_integer_and_display_semantics() {
    for (value, display, count) in [
        ("false", "False", 0),
        ("0", "False", 0),
        ("true", "True", 1),
        ("1", "True", 1),
    ] {
        let parameter = integer(
            Literal::new_typed_literal(value, iri(XSD, "boolean")).into(),
            "qualifiedMinCount",
        )
        .unwrap();
        assert_eq!(parameter.to_string(), display);
        assert_eq!(parameter.number, BigInt::from(count));
        assert!(parameter.allows(count, true));
        assert!(parameter.allows(count, false));
    }
    assert!(
        integer(
            Literal::new_typed_literal("invalid", iri(XSD, "boolean")).into(),
            "qualifiedMaxCount"
        )
        .is_err()
    );
    assert!(integer(iri("urn:", "notLiteral").into(), "minCount").is_err());
}

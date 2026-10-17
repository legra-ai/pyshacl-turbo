use super::*;
use oxigraph::model::BlankNode;

#[test]
fn flags_keep_rdflib_truth_and_lexical_semantics() {
    for value in ["false", "0"] {
        assert_eq!(
            flag_text(&Literal::new_typed_literal(value, xsd::BOOLEAN).into()),
            ""
        );
    }
    assert_eq!(flag_text(&Literal::new_simple_literal("ims").into()), "ims");
    assert_eq!(
        flag_text(&NamedNode::new("urn:ims").unwrap().into()),
        "urn:ims"
    );
    assert_eq!(flag_text(&BlankNode::new("ims").unwrap().into()), "ims");
    assert!(string(&NamedNode::new("urn:s").unwrap().into()).is_none());
    assert!(string(&Literal::from(3).into()).is_none());
    assert!(
        string(
            &Literal::new_language_tagged_literal("text", "fr")
                .unwrap()
                .into()
        )
        .is_some()
    );
}

fn rendered(source: &str, regex: &Regex) -> String {
    replacement(source, regex)
        .unwrap()
        .into_iter()
        .map(|piece| match piece {
            Replacement::Text(text) => text,
            Replacement::Group(index) => format!("[{index}]"),
        })
        .collect()
}

#[test]
fn replacement_escapes_preserve_python_control_octal_and_group_semantics() {
    let regex = Regex::new("(?P<word>a)(b)").unwrap();
    assert_eq!(
        rendered(r"\a\b\f\n\r\t\v\\\!", &regex),
        "\x07\x08\x0c\n\r\t\x0b\\\\!"
    );
    assert_eq!(rendered(r"\0\07\077\101", &regex), "\0\x07?A");
    assert_eq!(
        rendered(r"prefix$1:\g<word>:\g<0>", &regex),
        "prefix[1]:[1]:[0]"
    );
    assert_eq!(rendered(r"\089", &regex), "\089");
}

#[test]
fn malformed_replacements_fail_before_execution() {
    let regex = Regex::new("(a)").unwrap();
    for (source, expected) in [
        ("\\", "trailing backslash"),
        (r"\gX", "missing <"),
        (r"\g<word", "unterminated"),
        (r"\g<>", "empty group"),
        (r"\g<999999999999999999999999999999999999999>", "too large"),
        (r"\g<missing>", "unknown group name"),
        (r"\777", "exceeds"),
        (r"\q", "unknown escape"),
        (r"\99", "invalid group"),
    ] {
        assert!(
            replacement(source, &regex)
                .err()
                .unwrap()
                .to_string()
                .contains(expected),
            "{source}"
        );
    }
}

#[test]
fn scalar_callbacks_validate_arity_and_keep_the_pattern_cache_bounded() {
    let functions = RegexFunctions::default();
    assert!(functions.call(&[], false).unwrap().is_none());
    let literal = |value: &str| Term::from(Literal::new_simple_literal(value));
    assert!(
        functions
            .call(
                &[NamedNode::new("urn:s").unwrap().into(), literal("a")],
                false
            )
            .unwrap()
            .is_none()
    );
    assert!(
        functions
            .call(
                &[
                    literal("a"),
                    literal("a"),
                    NamedNode::new("urn:s").unwrap().into()
                ],
                true
            )
            .unwrap()
            .is_none()
    );
    let cached = functions.compiled("literal", "").unwrap();
    assert!(Arc::ptr_eq(
        &cached,
        &functions.compiled("literal", "").unwrap()
    ));
    for i in 0..CACHE_LIMIT + 3 {
        assert!(
            functions
                .compiled(&format!("literal{i}"), "")
                .unwrap()
                .is_match(&format!("literal{i}"))
                .unwrap()
        );
        assert!(functions.cache.lock().unwrap().len() <= CACHE_LIMIT);
    }
}

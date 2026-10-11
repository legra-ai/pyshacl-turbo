use std::collections::{HashMap, HashSet};
use std::fmt;
use std::sync::OnceLock;

use num_bigint::{BigInt, Sign};
use oxigraph::model::*;
use oxigraph::sparql::{PreparedSparqlQuery, SparqlEvaluator};
use regex_syntax::hir::{Class, ClassUnicode, HirKind};

use crate::graph::*;
use crate::path::rdf_list;
use crate::{Error, Result};

pub(crate) const PARAMETERS: &[&str] = &[
    "sparql",
    "minCount",
    "maxCount",
    "hasValue",
    "class",
    "datatype",
    "nodeKind",
    "minExclusive",
    "minInclusive",
    "maxExclusive",
    "maxInclusive",
    "minLength",
    "maxLength",
    "pattern",
    "flags",
    "languageIn",
    "uniqueLang",
    "equals",
    "disjoint",
    "lessThan",
    "lessThanOrEquals",
    "in",
    "closed",
    "ignoredProperties",
    "node",
    "not",
    "and",
    "or",
    "xone",
    "qualifiedValueShape",
    "qualifiedMinCount",
    "qualifiedMaxCount",
    "qualifiedValueShapesDisjoint",
];

pub(crate) enum Constraint {
    NodeExpression {
        expression: crate::expression::NodeExpression,
        node: Term,
        messages: Vec<Term>,
    },
    Sparql(Box<crate::sparql::SparqlConstraint>),
    Count {
        minimum: bool,
        count: IntegerParameter,
    },
    HasValue(Term),
    Class(Term),
    Datatype(NamedNode),
    NodeKind(String),
    Pattern(crate::pattern::Pattern),
    Expression {
        component: &'static str,
        query: Box<PreparedSparqlQuery>,
    },
    Length {
        minimum: bool,
        count: IntegerParameter,
    },
    LanguageIn(Vec<String>),
    UniqueLang,
    In(HashSet<Term>),
    Pair {
        kind: &'static str,
        predicate: NamedNode,
        query: Option<Box<PreparedSparqlQuery>>,
    },
    Logical {
        kind: &'static str,
        shapes: Vec<usize>,
    },
    Node(usize),
    Qualified {
        shape: usize,
        minimum: Option<IntegerParameter>,
        maximum: Option<IntegerParameter>,
        disjoint: bool,
        siblings: Vec<usize>,
    },
    Closed(HashSet<NamedNode>),
}

pub(crate) fn named(term: Term, context: &str) -> Result<NamedNode> {
    match term {
        Term::NamedNode(n) => Ok(n),
        _ => Err(Error::Invalid(format!("{context} requires an IRI"))),
    }
}

/// Keep the exact declaration alongside its arbitrary-precision comparison value.
pub(crate) struct IntegerParameter {
    pub literal: Literal,
    pub number: BigInt,
}

impl IntegerParameter {
    pub fn allows(&self, size: usize, minimum: bool) -> bool {
        let size = BigInt::from(size);
        if minimum {
            size >= self.number
        } else {
            size <= self.number
        }
    }

    pub fn is_zero(&self) -> bool {
        self.number.sign() == Sign::NoSign
    }
}

impl fmt::Display for IntegerParameter {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Python bool is an int subclass in qualified-count declarations.
        if self.literal.datatype() == iri(XSD, "boolean").as_ref() {
            f.write_str(if self.is_zero() { "False" } else { "True" })
        } else {
            self.number.fmt(f)
        }
    }
}

fn integer(term: Term, name: &str) -> Result<IntegerParameter> {
    let invalid = || Error::Invalid(format!("Invalid integer parameter sh:{name}: {term}"));
    let Term::Literal(literal) = &term else {
        return Err(invalid());
    };
    let kind = literal.datatype().as_str().strip_prefix(XSD);
    let qualified = matches!(name, "qualifiedMinCount" | "qualifiedMaxCount");
    let length = matches!(name, "minLength" | "maxLength");
    let number = if qualified && kind == Some("boolean") {
        match literal.value() {
            "true" | "1" => BigInt::from(1),
            "false" | "0" => BigInt::from(0),
            _ => return Err(invalid()),
        }
    } else {
        let integer_kind = matches!(
            kind,
            Some(
                "integer"
                    | "int"
                    | "long"
                    | "short"
                    | "byte"
                    | "unsignedLong"
                    | "unsignedInt"
                    | "unsignedShort"
                    | "unsignedByte"
                    | "nonNegativeInteger"
                    | "positiveInteger"
                    | "nonPositiveInteger"
                    | "negativeInteger"
            )
        );
        if !integer_kind
            || (!qualified && !length && kind != Some("integer"))
            // The pinned reference's length whitelist excludes xsd:byte as
            // well as the negative/nonpositive datatypes, even for zero.
            || (length && matches!(kind, Some("byte" | "negativeInteger" | "nonPositiveInteger")))
        {
            return Err(invalid());
        }
        integer_lexical(literal.value()).ok_or_else(invalid)?
    };
    if !qualified && number.sign() == Sign::Minus {
        return Err(invalid());
    }
    Ok(IntegerParameter {
        literal: literal.clone(),
        number,
    })
}

fn integer_lexical(text: &str) -> Option<BigInt> {
    // RDFLib uses Python int for these literals: decimal digits may be Unicode,
    // with one underscore between digits. BigInt's own parser is more lenient
    // about underscores, so validate and normalize before parsing its value.
    let mut chars = text.trim().chars().peekable();
    let mut normalized = String::with_capacity(text.len());
    if chars.peek().is_some_and(|ch| matches!(ch, '+' | '-')) {
        normalized.push(chars.next()?);
    }
    let mut after_digit = false;
    for ch in chars {
        if ch == '_' {
            if !after_digit {
                return None;
            }
            after_digit = false;
        } else {
            normalized.push(char::from(b'0' + decimal_digit(ch)?));
            after_digit = true;
        }
    }
    if !after_digit {
        return None;
    }
    normalized.parse().ok()
}

fn decimal_digit(ch: char) -> Option<u8> {
    if ch.is_ascii_digit() {
        return Some(ch as u8 - b'0');
    }
    static DIGITS: OnceLock<ClassUnicode> = OnceLock::new();
    let digits = DIGITS.get_or_init(|| {
        let hir = regex_syntax::Parser::new()
            .parse(r"\p{Nd}")
            .expect("Unicode decimal-digit class is valid");
        let HirKind::Class(Class::Unicode(class)) = hir.kind() else {
            unreachable!("decimal digits form a Unicode class");
        };
        class.clone()
    });
    let ranges = digits.ranges();
    let range = ranges.get(ranges.partition_point(|range| range.end() < ch))?;
    // Unicode Nd digits occur in consecutive runs of 0 through 9; adjacent
    // digit alphabets may share a range, hence the modulo operation.
    (range.start() <= ch).then(|| ((ch as u32 - range.start() as u32) % 10) as u8)
}

fn string(term: Term, name: &str) -> Result<String> {
    if let Term::Literal(v) = term
        && v.datatype() == iri(XSD, "string").as_ref()
    {
        return Ok(v.value().to_owned());
    }
    Err(Error::Invalid(format!("sh:{name} requires an xsd:string")))
}

fn expression(text: &str) -> Result<Box<PreparedSparqlQuery>> {
    Ok(Box::new(
        SparqlEvaluator::new()
            .parse_query(&format!("SELECT ?value ?other ({text} AS ?ok) WHERE {{}}"))
            .map_err(|e| Error::Invalid(format!("Constraint expression: {e}")))?,
    ))
}

pub(crate) fn shape_references(store: &Dataset) -> Result<HashSet<Term>> {
    let mut result = HashSet::new();
    for name in [
        "property",
        "condition",
        "node",
        "not",
        "qualifiedValueShape",
        "and",
        "or",
        "xone",
    ] {
        for node in subjects(store, &iri(SH, name), None)? {
            for target in values(store, &node, name)? {
                if ["and", "or", "xone"].contains(&name)
                    || (name == "condition"
                        && (target == Term::from(iri(RDF, "nil"))
                            || !objects(store, &target, &iri(RDF, "first"))?.is_empty()))
                {
                    result.extend(rdf_list(store, &target)?);
                } else {
                    result.insert(target);
                }
            }
        }
    }
    Ok(result)
}

pub(crate) fn compile(
    store: &Dataset,
    node: &Term,
    property: bool,
    indices: &HashMap<Term, usize>,
) -> Result<Vec<Constraint>> {
    let mut result = Vec::new();
    let reference = |n: &Term| -> Result<usize> {
        indices
            .get(n)
            .copied()
            .ok_or_else(|| Error::Invalid(format!("Unknown shape {n}")))
    };
    for (name, minimum) in [("minCount", true), ("maxCount", false)] {
        if let Some(value) = one(store, node, name)? {
            if !property {
                return Err(Error::Invalid(format!(
                    "sh:{name} requires a property shape"
                )));
            }
            result.push(Constraint::Count {
                minimum,
                count: integer(value, name)?,
            });
        }
    }
    result.extend(
        values(store, node, "hasValue")?
            .into_iter()
            .map(Constraint::HasValue),
    );
    for value in values(store, node, "class")? {
        result.push(Constraint::Class(named(value, "sh:class")?.into()));
    }
    if let Some(value) = one(store, node, "datatype")? {
        result.push(Constraint::Datatype(named(value, "sh:datatype")?));
    }
    if let Some(value) = one(store, node, "nodeKind")? {
        let kind = named(value, "sh:nodeKind")?;
        let name = kind.as_str().strip_prefix(SH).unwrap_or("");
        if ![
            "IRI",
            "BlankNode",
            "Literal",
            "BlankNodeOrIRI",
            "BlankNodeOrLiteral",
            "IRIOrLiteral",
        ]
        .contains(&name)
        {
            return Err(Error::Invalid(format!("Invalid sh:nodeKind {kind}")));
        }
        result.push(Constraint::NodeKind(name.to_owned()));
    }
    for (name, component, operator) in [
        ("minExclusive", "MinExclusiveConstraintComponent", ">"),
        ("minInclusive", "MinInclusiveConstraintComponent", ">="),
        ("maxExclusive", "MaxExclusiveConstraintComponent", "<"),
        ("maxInclusive", "MaxInclusiveConstraintComponent", "<="),
    ] {
        if let Some(value) = one(store, node, name)? {
            if !matches!(value, Term::Literal(_)) {
                return Err(Error::Invalid(format!("sh:{name} requires a literal")));
            }
            result.push(Constraint::Expression {
                component,
                query: expression(&format!("?value {operator} {value}"))?,
            });
        }
    }
    for (name, minimum) in [("minLength", true), ("maxLength", false)] {
        if let Some(value) = one(store, node, name)? {
            result.push(Constraint::Length {
                minimum,
                count: integer(value, name)?,
            });
        }
    }
    let flags = one(store, node, "flags")?
        .map(|v| string(v, "flags"))
        .transpose()?
        .unwrap_or_default();
    for pattern in values(store, node, "pattern")? {
        let Term::Literal(pattern) = pattern else {
            return Err(Error::Invalid("sh:pattern requires a literal".into()));
        };
        result.push(Constraint::Pattern(crate::pattern::Pattern::compile(
            pattern.value(),
            &flags,
        )?));
    }
    if let Some(head) = one(store, node, "languageIn")? {
        result.push(Constraint::LanguageIn(
            rdf_list(store, &head)?
                .into_iter()
                .map(|v| string(v, "languageIn").map(|v| v.to_ascii_lowercase()))
                .collect::<Result<_>>()?,
        ));
    }
    if boolean(store, node, "uniqueLang")? {
        if !property {
            return Err(Error::Invalid(
                "sh:uniqueLang requires a property shape".into(),
            ));
        }
        result.push(Constraint::UniqueLang);
    }
    if let Some(head) = one(store, node, "in")? {
        result.push(Constraint::In(
            rdf_list(store, &head)?.into_iter().collect(),
        ));
    }
    for (name, kind, operator) in [
        ("equals", "EqualsConstraintComponent", None),
        ("disjoint", "DisjointConstraintComponent", None),
        ("lessThan", "LessThanConstraintComponent", Some("<")),
        (
            "lessThanOrEquals",
            "LessThanOrEqualsConstraintComponent",
            Some("<="),
        ),
    ] {
        for value in values(store, node, name)? {
            if operator.is_some() && !property {
                return Err(Error::Invalid(format!(
                    "sh:{name} requires a property shape"
                )));
            }
            result.push(Constraint::Pair {
                kind,
                predicate: named(value, name)?,
                query: operator
                    .map(|op| expression(&format!("?value {op} ?other")))
                    .transpose()?,
            });
        }
    }
    for value in values(store, node, "node")? {
        result.push(Constraint::Node(reference(&value)?));
    }
    for (name, kind) in [
        ("not", "NotConstraintComponent"),
        ("and", "AndConstraintComponent"),
        ("or", "OrConstraintComponent"),
        ("xone", "XoneConstraintComponent"),
    ] {
        for value in values(store, node, name)? {
            let terms = if name == "not" {
                vec![value]
            } else {
                rdf_list(store, &value)?
            };
            result.push(Constraint::Logical {
                kind,
                shapes: terms.iter().map(reference).collect::<Result<_>>()?,
            });
        }
    }
    let minimum = one(store, node, "qualifiedMinCount")?
        .map(|n| integer(n, "qualifiedMinCount"))
        .transpose()?;
    let maximum = one(store, node, "qualifiedMaxCount")?
        .map(|n| integer(n, "qualifiedMaxCount"))
        .transpose()?;
    let disjoint = boolean(store, node, "qualifiedValueShapesDisjoint")?;
    if let Some(value) = one(store, node, "qualifiedValueShape")? {
        if !property {
            return Err(Error::Invalid(
                "sh:qualifiedValueShape requires a property shape".into(),
            ));
        }
        let mut siblings = HashSet::new();
        if disjoint {
            for parent in subjects(store, &iri(SH, "property"), Some(node))? {
                for sibling in values(store, &parent, "property")? {
                    for qualified in values(store, &sibling, "qualifiedValueShape")? {
                        if qualified != value {
                            siblings.insert(reference(&qualified)?);
                        }
                    }
                }
            }
        }
        result.push(Constraint::Qualified {
            shape: reference(&value)?,
            minimum,
            maximum,
            disjoint,
            siblings: siblings.into_iter().collect(),
        });
        // Qualified counts do not activate a constraint without qualifiedValueShape.
        // W3C core/node/qualified-001 explicitly permits these parameters on a node shape.
    }
    let ignored = one(store, node, "ignoredProperties")?;
    if ignored.is_some() && one(store, node, "closed")?.is_none() {
        return Err(Error::Invalid(
            "sh:ignoredProperties requires sh:closed".into(),
        ));
    }
    let ignored = ignored
        .map(|head| rdf_list(store, &head))
        .transpose()?
        .unwrap_or_default();
    let mut allowed: HashSet<_> = ignored
        .into_iter()
        .map(|v| named(v, "sh:ignoredProperties"))
        .collect::<Result<_>>()?;
    if boolean(store, node, "closed")? {
        for property in values(store, node, "property")? {
            if let Some(Term::NamedNode(path)) = one(store, &property, "path")? {
                allowed.insert(path);
            }
        }
        result.push(Constraint::Closed(allowed));
    }
    Ok(result)
}

#[cfg(test)]
mod integer_tests {
    use super::*;

    #[test]
    fn invalid_integer_parameters_return_errors_without_panicking() {
        for lexical in ["no", "²", "١٢x", "1.0"] {
            let term = Literal::new_typed_literal(lexical, iri(XSD, "integer"));
            assert!(integer(term.into(), "minCount").is_err());
        }
    }
}

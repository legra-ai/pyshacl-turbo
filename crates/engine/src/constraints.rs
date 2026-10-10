use std::collections::{HashMap, HashSet};

use oxigraph::model::*;
use oxigraph::sparql::{PreparedSparqlQuery, SparqlEvaluator};

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
        count: u64,
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
        count: u64,
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
        minimum: Option<u64>,
        maximum: Option<u64>,
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

fn integer(term: Term, name: &str) -> Result<u64> {
    if let Term::Literal(v) = term
        && v.datatype() == iri(XSD, "integer").as_ref()
        && let Ok(n) = v.value().parse()
    {
        return Ok(n);
    }
    Err(Error::Invalid(format!(
        "sh:{name} requires a nonnegative 64-bit xsd:integer"
    )))
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

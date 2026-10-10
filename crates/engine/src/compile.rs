use std::collections::{HashMap, HashSet};

use crate::expression::NodeExpression;
use crate::functions::{Functions, NativeQuery};
use bigdecimal::BigDecimal;
use oxigraph::model::*;
use spargebra::algebra::GraphPattern;
use spargebra::{Query, SparqlParser};

use crate::constraints::{self, Constraint, named};
use crate::graph::*;
use crate::path::{Path, rdf_list};
use crate::{Error, Result};

pub(crate) enum Target {
    Node(Term),
    Class(Term),
    Subjects(NamedNode),
    Objects(NamedNode),
    Sparql {
        query: Box<NativeQuery>,
        bindings: Vec<(Variable, Term)>,
    },
}

pub(crate) struct Rule {
    pub node: Term,
    pub order: BigDecimal,
    pub deactivated: bool,
    pub conditions: Vec<usize>,
    pub queries: Vec<NativeQuery>,
    pub triple: Option<[NodeExpression; 3]>,
}

pub(crate) struct Shape {
    pub node: Term,
    pub path: Option<Path>,
    pub path_node: Option<Term>,
    pub order: BigDecimal,
    pub deactivated: bool,
    pub targets: Vec<Target>,
    pub constraints: Vec<Constraint>,
    pub properties: Vec<usize>,
    pub rules: Vec<Rule>,
    pub messages: Vec<Term>,
    pub severity: NamedNode,
}

/// Immutable compiled shapes and SPARQL queries; safe to share across validations.
pub struct CompiledShapes {
    pub(crate) graph: Dataset,
    pub(crate) shapes: Vec<Shape>,
    pub(crate) execution_order: Vec<usize>,
    pub(crate) functions: Functions,
    pub(crate) namespaces: Vec<(String, String)>,
}

fn order(store: &Dataset, node: &Term) -> Result<BigDecimal> {
    match one(store, node, "order")? {
        None => Ok(BigDecimal::from(0)),
        Some(Term::Literal(v))
            if ["integer", "decimal", "float", "double"]
                .iter()
                .any(|t| v.datatype() == iri(XSD, t).as_ref()) =>
        {
            v.value()
                .parse()
                .map_err(|_| Error::Invalid(format!("Invalid sh:order on {node}")))
        }
        _ => Err(Error::Invalid(format!(
            "sh:order must be numeric on {node}"
        ))),
    }
}

fn query(
    store: &Dataset,
    node: &Term,
    term: &Term,
    construct: bool,
    namespaces: &[(String, String)],
) -> Result<NativeQuery> {
    let Term::Literal(text) = term else {
        return Err(Error::Invalid(
            "SPARQL query must be a string literal".into(),
        ));
    };
    if text.datatype() != iri(XSD, "string").as_ref() {
        return Err(Error::Invalid("SPARQL query must be an xsd:string".into()));
    }
    let mut parsed = SparqlParser::new()
        .parse_query(&format!(
            "{}\n{}",
            crate::sparql::prefixes(store, node, namespaces)?,
            text.value()
        ))
        .map_err(|e| Error::Invalid(format!("SPARQL parse error: {e}")))?;
    if (construct && !matches!(parsed, Query::Construct { .. }))
        || (!construct && !matches!(parsed, Query::Select { .. }))
    {
        return Err(Error::Invalid(format!(
            "SPARQL query must be {}",
            if construct { "CONSTRUCT" } else { "SELECT" }
        )));
    }
    match &mut parsed {
        Query::Select { pattern, .. } => {
            let mut has_this = false;
            pattern.on_in_scope_variable(|v| has_this |= v.as_str() == "this");
            if !has_this {
                return Err(Error::Invalid("SPARQL target must project ?this".into()));
            }
        }
        Query::Construct { pattern, .. } => {
            // Oxigraph substitutions require a projected variable. Make the
            // SHACL prebinding explicit in the algebra, even when $this occurs
            // only in a filter/template or is absent from a constant rule.
            let mut variables = HashSet::new();
            pattern.on_in_scope_variable(|v| {
                variables.insert(v.clone());
            });
            variables.insert(Variable::new_unchecked("this"));
            *pattern = GraphPattern::Project {
                inner: Box::new(pattern.clone()),
                variables: variables.into_iter().collect(),
            };
        }
        _ => unreachable!("Query kind was checked above"),
    }
    Ok(NativeQuery::new(parsed))
}

fn check_vocabulary(
    store: &Dataset,
    advanced: bool,
    executable_nodes: &HashSet<Term>,
) -> Result<()> {
    // Deliberately closed for the experimental milestone. This also catches
    // misspelled SHACL terms instead of silently treating them as annotations.
    const ALLOWED: &[&str] = &[
        "targetNode",
        "targetClass",
        "targetSubjectsOf",
        "targetObjectsOf",
        "target",
        "select",
        "prefixes",
        "property",
        "path",
        "minCount",
        "maxCount",
        "hasValue",
        "message",
        "severity",
        "deactivated",
        "order",
        "rule",
        "condition",
        "construct",
        "name",
        "description",
        "group",
        "defaultValue",
        "nodeKind",
        "optional",
        "parameter",
        "validator",
        "nodeValidator",
        "propertyValidator",
        "ask",
        "labelTemplate",
        "label",
        "keyParameter",
        "returnType",
        "subject",
        "predicate",
        "object",
        "expression",
        "filterShape",
        "nodes",
        "union",
        "intersection",
    ];
    for quad in store.iter() {
        let quad = quad.into_owned();
        // Function/component declarations have implicit global registration.
        if advanced
            && quad.predicate == iri(RDF, "type")
            && let Term::NamedNode(ref n) = quad.object
            && let Some(name) = n.as_str().strip_prefix(SH)
            && ["Function", "SHACLFunction", "JSFunction"].contains(&name)
        {
            return Err(Error::Unsupported(format!("sh:{name}")));
        }
        // A shapes graph may also contain ordinary data and prior reports.
        // Only executable resources determine the supported SHACL program.
        if !executable_nodes.contains(&Term::from(quad.subject.clone())) {
            continue;
        }
        if let Some(name) = quad.predicate.as_str().strip_prefix(SH) {
            if !ALLOWED.contains(&name) && !constraints::PARAMETERS.contains(&name) {
                return Err(Error::Unsupported(format!("sh:{name} on {}", quad.subject)));
            }
            if !advanced && ["target", "rule", "construct", "condition"].contains(&name) {
                return Err(Error::Unsupported(format!(
                    "sh:{name} requires advanced=True"
                )));
            }
        }
        if quad.predicate == iri(RDF, "type")
            && let Term::NamedNode(ref n) = quad.object
            && let Some(name) = n.as_str().strip_prefix(SH)
            && ![
                "NodeShape",
                "PropertyShape",
                "SPARQLRule",
                "SPARQLTarget",
                "SPARQLConstraint",
                "ConstraintComponent",
                "Parameter",
                "SPARQLAskValidator",
                "SPARQLSelectValidator",
                "SPARQLFunction",
                "TripleRule",
                "SPARQLTargetType",
                "TargetType",
                "SPARQLConstraintObject",
            ]
            .contains(&name)
        {
            return Err(Error::Unsupported(format!("sh:{name}")));
        }
    }
    Ok(())
}

impl CompiledShapes {
    pub fn compile(store: Dataset, advanced: bool) -> Result<Self> {
        Self::compile_with_boolean_policy(store, advanced, true)
    }

    pub fn compile_with_boolean_policy(
        store: Dataset,
        advanced: bool,
        numeric_booleans: bool,
    ) -> Result<Self> {
        Self::compile_with_namespaces(store, advanced, numeric_booleans, &[])
    }

    pub fn compile_with_namespaces(
        mut store: Dataset,
        advanced: bool,
        numeric_booleans: bool,
        namespaces: &[(String, String)],
    ) -> Result<Self> {
        let original = store.clone();
        if !numeric_booleans {
            let replaced: Vec<_> = store.iter().filter(|q| {
                ["closed", "uniqueLang", "deactivated", "qualifiedValueShapesDisjoint", "optional"].iter().any(|p| q.predicate == iri(SH, p).as_ref())
                    && matches!(q.object, TermRef::Literal(l) if l.datatype() == iri(XSD, "boolean").as_ref() && l.value() == "1")
            }).map(|q| q.into_owned()).collect();
            for mut quad in replaced {
                store.remove(&quad);
                quad.object = Literal::from(false).into();
                store.insert(&quad);
            }
        }
        if store.iter().any(|q| !q.graph_name.is_default_graph()) {
            return Err(Error::Unsupported("named shapes graphs".into()));
        }
        // Validate all path descriptions, including standalone declarations,
        // without treating their subjects as executable shapes.
        let mut paths = HashMap::new();
        for q in store.quads_for_pattern(None, Some(iri(SH, "path").as_ref()), None, None) {
            let node = q.object.into_owned();
            if let std::collections::hash_map::Entry::Vacant(entry) = paths.entry(node.clone()) {
                entry.insert(Path::compile(&store, &node)?);
            }
        }
        let components = crate::components::Component::discover(&store)?;
        let functions = if advanced {
            Functions::compile(&store, namespaces)?
        } else {
            Functions::default()
        };
        let mut nodes = HashSet::new();
        for kind in ["NodeShape", "PropertyShape"] {
            nodes.extend(subjects(
                &store,
                &iri(RDF, "type"),
                Some(&iri(SH, kind).into()),
            )?);
        }
        for name in [
            "targetNode",
            "targetClass",
            "targetSubjectsOf",
            "targetObjectsOf",
            "target",
            "rule",
        ] {
            nodes.extend(subjects(&store, &iri(SH, name), None)?);
        }
        let mut parameters = instances(&store, &iri(SH, "Parameter").into())?;
        parameters.extend(
            store
                .quads_for_pattern(None, Some(iri(SH, "parameter").as_ref()), None, None)
                .map(|q| q.object.into_owned()),
        );
        for name in ["property", "node"] {
            // Parameter declarations can describe their argument with sh:node
            // or sh:property. This metadata is not a validation entry point.
            // An explicit shape type, target or shape reference still gives a
            // parameter a second, executable role.
            nodes.extend(
                subjects(&store, &iri(SH, name), None)?
                    .into_iter()
                    .filter(|n| !parameters.contains(n)),
            );
        }
        nodes.extend(constraints::shape_references(&store)?);
        for quad in store.quads_for_pattern(None, Some(iri(SH, "filterShape").as_ref()), None, None)
        {
            nodes.insert(quad.object.into_owned());
        }
        let mut executable_nodes = nodes.clone();
        for node in &nodes {
            for predicate in ["rule", "target", "sparql"] {
                executable_nodes.extend(values(&store, node, predicate)?);
            }
        }
        for component in &components {
            executable_nodes.insert(component.node.clone().into());
            executable_nodes.extend(component.parameters.iter().map(|p| p.node.clone()));
            executable_nodes.extend(component.validators.iter().cloned());
        }
        // Shape roles come from types, targets and shape-expecting predicates.
        // Constraint parameter annotations alone do not turn metadata into an
        // executable shape (e.g. sh:path on a function/component parameter).
        executable_nodes.extend(nodes.iter().cloned());
        check_vocabulary(&store, advanced, &executable_nodes)?;
        let mut nodes: Vec<_> = nodes.into_iter().collect();
        nodes.sort_by_key(ToString::to_string);
        let indices: HashMap<_, _> = nodes.iter().cloned().zip(0..).collect();
        let mut shapes = Vec::new();
        for node in nodes {
            subject(&node)?;
            let path_node = one(&store, &node, "path")?;
            let path = path_node.as_ref().map(|n| paths[n].clone());
            let types = objects(&store, &node, &iri(RDF, "type"))?;
            if types.contains(&iri(SH, "NodeShape").into()) && path.is_some() {
                return Err(Error::Invalid(format!(
                    "NodeShape {node} cannot have sh:path"
                )));
            }
            if types.contains(&iri(SH, "PropertyShape").into()) && path.is_none() {
                return Err(Error::Invalid(format!(
                    "PropertyShape {node} requires sh:path"
                )));
            }
            let mut targets = Vec::new();
            targets.extend(
                values(&store, &node, "targetNode")?
                    .into_iter()
                    .map(Target::Node),
            );
            for term in values(&store, &node, "targetClass")? {
                targets.push(Target::Class(named(term, "sh:targetClass")?.into()));
            }
            if types.contains(&iri(RDFS, "Class").into())
                || types.contains(&iri("http://www.w3.org/2002/07/owl#", "Class").into())
            {
                targets.push(Target::Class(node.clone()));
            }
            for term in values(&store, &node, "targetSubjectsOf")? {
                targets.push(Target::Subjects(named(term, "sh:targetSubjectsOf")?));
            }
            for term in values(&store, &node, "targetObjectsOf")? {
                targets.push(Target::Objects(named(term, "sh:targetObjectsOf")?));
            }
            for target in values(&store, &node, "target")? {
                let types = objects(&store, &target, &iri(RDF, "type"))?;
                let (definition, bindings) = if types.contains(&iri(SH, "SPARQLTarget").into()) {
                    (target.clone(), Vec::new())
                } else {
                    let definition = types
                        .iter()
                        .find(|t| {
                            objects(&store, t, &iri(RDF, "type"))
                                .is_ok_and(|v| v.contains(&iri(SH, "SPARQLTargetType").into()))
                        })
                        .ok_or_else(|| Error::Unsupported(format!("target type on {target}")))?
                        .clone();
                    let mut bindings = Vec::new();
                    for parameter in crate::functions::parameters(&store, &definition)? {
                        let values = objects(&store, &target, &parameter.path)?;
                        if values.len() > 1 || (values.is_empty() && !parameter.optional) {
                            return Err(Error::Invalid(format!(
                                "Target {target} requires one value for {}",
                                parameter.path
                            )));
                        }
                        if let Some(value) = values.into_iter().next() {
                            bindings.push((parameter.variable, value));
                        }
                    }
                    (definition, bindings)
                };
                let text = one(&store, &definition, "select")?
                    .ok_or_else(|| Error::Invalid(format!("Missing sh:select on {definition}")))?;
                let mut parsed = query(&store, &definition, &text, false, namespaces)?.parsed;
                crate::functions::project_bindings(
                    &mut parsed,
                    &bindings.iter().map(|(v, _)| v.clone()).collect::<Vec<_>>(),
                );
                targets.push(Target::Sparql {
                    query: Box::new(NativeQuery::new(parsed)),
                    bindings,
                });
            }
            let mut constraints = constraints::compile(&store, &node, path.is_some(), &indices)?;
            for expression in values(&store, &node, "expression")? {
                if !advanced {
                    return Err(Error::Unsupported(
                        "sh:expression requires advanced=True".into(),
                    ));
                }
                constraints.push(Constraint::NodeExpression {
                    expression: NodeExpression::compile(&store, &expression, &indices, &functions)?,
                    messages: values(&store, &expression, "message")?,
                    node: expression,
                });
            }
            for constraint in values(&store, &node, "sparql")? {
                constraints.push(Constraint::Sparql(Box::new(crate::sparql::compile(
                    &store,
                    &constraint,
                    path.as_ref(),
                    namespaces,
                )?)));
            }
            for component in &components {
                constraints.extend(component.compile(&store, &node, path.as_ref(), namespaces)?);
            }
            let properties: Vec<_> = values(&store, &node, "property")?
                .iter()
                .map(|n| {
                    indices
                        .get(n)
                        .copied()
                        .ok_or_else(|| Error::Invalid("Unknown property shape".into()))
                })
                .collect::<Result<_>>()?;
            let mut rules = Vec::new();
            for rule in values(&store, &node, "rule")? {
                let types = objects(&store, &rule, &iri(RDF, "type"))?;
                let (queries, triple) = if types.contains(&iri(SH, "SPARQLRule").into()) {
                    let queries = values(&store, &rule, "construct")?
                        .iter()
                        .map(|text| query(&store, &rule, text, true, namespaces))
                        .collect::<Result<Vec<_>>>()?;
                    if queries.is_empty() {
                        return Err(Error::Invalid(format!("Missing sh:construct on {rule}")));
                    }
                    (queries, None)
                } else if types.contains(&iri(SH, "TripleRule").into()) {
                    let mut exprs = Vec::new();
                    for p in ["subject", "predicate", "object"] {
                        let n = one(&store, &rule, p)?
                            .ok_or_else(|| Error::Invalid(format!("TripleRule requires sh:{p}")))?;
                        exprs.push(NodeExpression::compile(&store, &n, &indices, &functions)?);
                    }
                    (
                        Vec::new(),
                        Some(exprs.try_into().unwrap_or_else(|_| unreachable!())),
                    )
                } else {
                    return Err(Error::Unsupported(format!("rule type on {rule}")));
                };
                let mut condition_nodes = Vec::new();
                for value in values(&store, &rule, "condition")? {
                    if value == Term::from(iri(RDF, "nil"))
                        || !objects(&store, &value, &iri(RDF, "first"))?.is_empty()
                    {
                        condition_nodes.extend(rdf_list(&store, &value)?);
                    } else {
                        condition_nodes.push(value);
                    }
                }
                let conditions = condition_nodes
                    .iter()
                    .map(|n| {
                        indices
                            .get(n)
                            .copied()
                            .ok_or_else(|| Error::Invalid("Unknown condition shape".into()))
                    })
                    .collect::<Result<_>>()?;
                rules.push(Rule {
                    node: rule.clone(),
                    order: order(&store, &rule)?,
                    deactivated: boolean(&store, &rule, "deactivated")?,
                    conditions,
                    queries,
                    triple,
                });
            }
            rules.sort_by(|a, b| {
                a.order
                    .cmp(&b.order)
                    .then_with(|| a.node.to_string().cmp(&b.node.to_string()))
            });
            let messages = values(&store, &node, "message")?;
            if messages.iter().any(|m| !matches!(m, Term::Literal(_))) {
                return Err(Error::Invalid(format!(
                    "sh:message must be a literal on {node}"
                )));
            }
            let severity = one(&store, &node, "severity")?
                .map(|n| named(n, "sh:severity"))
                .transpose()?
                .unwrap_or_else(|| iri(SH, "Violation"));
            shapes.push(Shape {
                order: order(&store, &node)?,
                deactivated: boolean(&store, &node, "deactivated")?,
                node,
                path,
                path_node,
                targets,
                constraints,
                properties,
                rules,
                messages,
                severity,
            });
        }
        for shape in &shapes {
            for &p in &shape.properties {
                if shapes[p].path.is_none() {
                    return Err(Error::Invalid(format!(
                        "sh:property points to {} without sh:path",
                        shapes[p].node
                    )));
                }
            }
        }
        let mut execution_order: Vec<_> = (0..shapes.len()).collect();
        execution_order.sort_by(|&a, &b| shapes[a].order.cmp(&shapes[b].order));
        Ok(Self {
            graph: original,
            shapes,
            execution_order,
            functions,
            namespaces: namespaces.to_vec(),
        })
    }
}

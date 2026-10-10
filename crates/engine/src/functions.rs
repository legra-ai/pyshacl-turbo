//! Native SHACL functions and query preparation with per-evaluation registration.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use bigdecimal::BigDecimal;
use oxigraph::model::*;
use oxigraph::sparql::{
    PreparedSparqlQuery, QueryEvaluationError, QueryResults, QuerySolutionIter, QueryTripleIter,
    SparqlEvaluator,
};
use spargebra::{Query, SparqlParser, algebra::GraphPattern};

use crate::graph::*;
use crate::{Error, Result};

pub(crate) struct NativeQuery {
    pub parsed: Query,
    prepared: PreparedSparqlQuery,
}

impl NativeQuery {
    pub fn new(parsed: Query) -> Self {
        Self {
            prepared: SparqlEvaluator::new().for_query(parsed.clone()),
            parsed,
        }
    }

    pub fn prepare(&self, functions: &Functions, data: &Dataset) -> NativePrepared {
        if functions.0.is_empty() {
            NativePrepared {
                query: self.prepared.clone(),
                errors: None,
            }
        } else {
            let errors = Arc::new(Mutex::new(None));
            NativePrepared {
                query: functions
                    .evaluator(Arc::new(data.clone()), 0, errors.clone())
                    .for_query(self.parsed.clone()),
                errors: Some(errors),
            }
        }
    }
}

type FunctionErrors = Arc<Mutex<Option<Error>>>;

pub(crate) struct NativePrepared {
    query: PreparedSparqlQuery,
    errors: Option<FunctionErrors>,
}

impl NativePrepared {
    pub fn on_queryable_dataset(self, data: &Dataset) -> NativeBound<'_> {
        NativeBound {
            prepared: self,
            data,
            bindings: Vec::new(),
        }
    }
}

pub(crate) struct NativeBound<'a> {
    prepared: NativePrepared,
    data: &'a Dataset,
    bindings: Vec<(Variable, Term)>,
}

impl<'a> NativeBound<'a> {
    pub fn substitute_variable(mut self, variable: Variable, term: impl Into<Term>) -> Self {
        self.bindings.push((variable, term.into()));
        self
    }

    pub fn execute(self) -> Result<QueryResults<'a>> {
        let mut query = self.prepared.query.on_queryable_dataset(self.data);
        for (variable, value) in self.bindings {
            query = query.substitute_variable(variable, value);
        }
        let result = query.execute()?;
        let Some(errors) = self.prepared.errors else {
            return Ok(result);
        };
        if let Some(error) = errors.lock().expect("function error mutex poisoned").take() {
            return Err(error);
        }
        Ok(match result {
            QueryResults::Solutions(rows) => QueryResults::Solutions(QuerySolutionIter::new(
                rows.variables().to_vec().into(),
                Checked {
                    inner: rows,
                    errors,
                    done: false,
                },
            )),
            QueryResults::Graph(triples) => QueryResults::Graph(QueryTripleIter::new(Checked {
                inner: triples,
                errors,
                done: false,
            })),
            QueryResults::Boolean(value) => QueryResults::Boolean(value),
        })
    }
}

struct Checked<I> {
    inner: I,
    errors: FunctionErrors,
    done: bool,
}

impl<T, I: Iterator<Item = std::result::Result<T, QueryEvaluationError>>> Iterator for Checked<I> {
    type Item = std::result::Result<T, QueryEvaluationError>;
    fn next(&mut self) -> Option<Self::Item> {
        if self.done {
            return None;
        }
        let next = self.inner.next();
        if let Some(error) = self
            .errors
            .lock()
            .expect("function error mutex poisoned")
            .take()
        {
            self.done = true;
            return Some(Err(QueryEvaluationError::Unexpected(Box::new(error))));
        }
        self.done = next.is_none();
        next
    }
}

pub(crate) struct Parameter {
    pub path: NamedNode,
    pub variable: Variable,
    pub optional: bool,
}

pub(crate) fn parameters(graph: &Dataset, node: &Term) -> Result<Vec<Parameter>> {
    let mut parameters = Vec::new();
    for p in values(graph, node, "parameter")? {
        let path = crate::constraints::named(
            one(graph, &p, "path")?
                .ok_or_else(|| Error::Invalid("SHACL parameter requires sh:path".into()))?,
            "Parameter path",
        )?;
        let name = path.as_str().rsplit(['#', '/']).next().unwrap();
        let variable = Variable::new(name).map_err(|e| Error::Invalid(e.to_string()))?;
        let order = one(graph, &p, "order")?
            .map(|term| match term {
                Term::Literal(l) => l
                    .value()
                    .parse::<BigDecimal>()
                    .map_err(|e| Error::Invalid(e.to_string())),
                _ => Err(Error::Invalid("Parameter order must be numeric".into())),
            })
            .transpose()?;
        parameters.push((
            order,
            Parameter {
                path,
                variable,
                optional: boolean(graph, &p, "optional")?,
            },
        ));
    }
    let ordered = parameters.iter().all(|(o, _)| o.is_some());
    parameters.sort_by(|(a, x), (b, y)| {
        if ordered {
            a.cmp(b)
        } else {
            x.variable.as_str().cmp(y.variable.as_str())
        }
    });
    Ok(parameters.into_iter().map(|(_, p)| p).collect())
}

/// Make externally supplied variables available through the query's projection.
pub(crate) fn project_bindings(query: &mut Query, bindings: &[Variable]) {
    fn extend(pattern: &mut GraphPattern, bindings: &[Variable]) {
        match pattern {
            GraphPattern::Project { variables, .. } => {
                for v in bindings {
                    if !variables.contains(v) {
                        variables.push(v.clone());
                    }
                }
            }
            GraphPattern::Distinct { inner }
            | GraphPattern::Reduced { inner }
            | GraphPattern::Slice { inner, .. }
            | GraphPattern::OrderBy { inner, .. } => extend(inner, bindings),
            _ => {
                let mut variables = Vec::new();
                pattern.on_in_scope_variable(|v| variables.push(v.clone()));
                for v in bindings {
                    if !variables.contains(v) {
                        variables.push(v.clone());
                    }
                }
                *pattern = GraphPattern::Project {
                    inner: Box::new(pattern.clone()),
                    variables,
                };
            }
        }
    }
    match query {
        Query::Select { pattern, .. }
        | Query::Ask { pattern, .. }
        | Query::Construct { pattern, .. }
        | Query::Describe { pattern, .. } => extend(pattern, bindings),
    }
}

struct Function {
    query: Query,
    parameters: Vec<Parameter>,
    output: Option<Variable>,
}

#[derive(Clone, Default)]
pub(crate) struct Functions(Arc<HashMap<NamedNode, Function>>);

impl Functions {
    pub fn compile(graph: &Dataset, namespaces: &[(String, String)]) -> Result<Self> {
        let mut functions = HashMap::new();
        for node in subjects(
            graph,
            &iri(RDF, "type"),
            Some(&iri(SH, "SPARQLFunction").into()),
        )? {
            let name = crate::constraints::named(node.clone(), "SHACL function")?;
            let select = one(graph, &node, "select")?;
            let ask = one(graph, &node, "ask")?;
            let (text, is_ask) = match (select, ask) {
                (Some(Term::Literal(l)), None) => (l, false),
                (None, Some(Term::Literal(l))) => (l, true),
                _ => {
                    return Err(Error::Invalid(format!(
                        "Function {node} requires exactly one sh:select or sh:ask"
                    )));
                }
            };
            let parameters = parameters(graph, &node)?;
            let mut query = SparqlParser::new()
                .parse_query(&format!(
                    "{}\n{}",
                    crate::sparql::prefixes(graph, &node, namespaces)?,
                    text.value()
                ))
                .map_err(|e| Error::Invalid(format!("SPARQL function parse error: {e}")))?;
            let output = match &query {
                Query::Select { pattern, .. } if !is_ask => {
                    let mut first = None;
                    pattern.on_in_scope_variable(|v| {
                        if first.is_none() {
                            first = Some(v.clone());
                        }
                    });
                    Some(first.ok_or_else(|| {
                        Error::Invalid(format!("Function {node} must select a result variable"))
                    })?)
                }
                Query::Ask { .. } if is_ask => None,
                _ => {
                    return Err(Error::Invalid(format!(
                        "Function {node} query kind does not match its SHACL declaration"
                    )));
                }
            };
            project_bindings(
                &mut query,
                &parameters
                    .iter()
                    .map(|p| p.variable.clone())
                    .collect::<Vec<_>>(),
            );
            functions.insert(
                name,
                Function {
                    query,
                    parameters,
                    output,
                },
            );
        }
        Ok(Self(Arc::new(functions)))
    }

    pub fn contains(&self, name: &NamedNode) -> bool {
        self.0.contains_key(name)
    }

    fn evaluator(
        &self,
        data: Arc<Dataset>,
        depth: usize,
        errors: FunctionErrors,
    ) -> SparqlEvaluator {
        let mut evaluator = SparqlEvaluator::new();
        for name in self.0.keys() {
            let (functions, data, function) = (self.clone(), data.clone(), name.clone());
            let errors = errors.clone();
            evaluator = evaluator.with_custom_function(name.clone(), move |args| {
                if errors
                    .lock()
                    .expect("function error mutex poisoned")
                    .is_some()
                {
                    return None;
                }
                match functions.call_inner(&function, args, data.clone(), depth + 1) {
                    Ok(value) => value,
                    Err(error) => {
                        *errors.lock().expect("function error mutex poisoned") = Some(error);
                        None
                    }
                }
            });
        }
        evaluator
    }

    pub fn call(&self, name: &NamedNode, args: &[Term], data: &Dataset) -> Result<Option<Term>> {
        self.call_inner(name, args, Arc::new(data.clone()), 0)
    }

    fn call_inner(
        &self,
        name: &NamedNode,
        args: &[Term],
        data: Arc<Dataset>,
        depth: usize,
    ) -> Result<Option<Term>> {
        if depth >= 64 {
            return Err(Error::Runtime(
                "SHACL function recursion limit exceeded".into(),
            ));
        }
        let function = self
            .0
            .get(name)
            .ok_or_else(|| Error::Invalid(format!("Unknown SHACL function {name}")))?;
        if args.len() > function.parameters.len()
            || function
                .parameters
                .iter()
                .skip(args.len())
                .any(|p| !p.optional)
        {
            return Err(Error::Invalid(format!(
                "Wrong argument count for SHACL function {name}"
            )));
        }
        let errors = Arc::new(Mutex::new(None));
        let mut query = NativePrepared {
            query: self
                .evaluator(data.clone(), depth, errors.clone())
                .for_query(function.query.clone()),
            errors: Some(errors),
        }
        .on_queryable_dataset(data.as_ref());
        for (p, arg) in function.parameters.iter().zip(args) {
            query = query.substitute_variable(p.variable.clone(), arg.clone());
        }
        match query.execute()? {
            QueryResults::Boolean(value) => Ok(Some(Literal::from(value).into())),
            QueryResults::Solutions(mut rows) => Ok(rows
                .next()
                .transpose()?
                .and_then(|row| row.get(function.output.as_ref().unwrap()).cloned())),
            _ => Err(Error::Invalid(
                "SHACL function must return SELECT or ASK results".into(),
            )),
        }
    }
}

/// Execute a query with SHACL functions declared in the supplied shapes graph.
pub fn evaluate_query<'a>(
    data: &'a Dataset,
    shapes: &Dataset,
    query: &str,
    namespaces: &[(String, String)],
) -> Result<QueryResults<'a>> {
    let functions = Functions::compile(shapes, namespaces)?;
    let parsed = SparqlParser::new()
        .parse_query(query)
        .map_err(|e| Error::Invalid(format!("SPARQL parse error: {e}")))?;
    NativeQuery::new(parsed)
        .prepare(&functions, data)
        .on_queryable_dataset(data)
        .execute()
}

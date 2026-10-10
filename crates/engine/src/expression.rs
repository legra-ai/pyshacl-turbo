use std::collections::{HashMap, HashSet};

use oxigraph::model::*;

use crate::functions::Functions;
use crate::graph::*;
use crate::path::{Path, rdf_list};
use crate::{Error, Result};

pub(crate) enum NodeExpression {
    This,
    Constant(Term),
    Path(Path),
    Union(Vec<Self>),
    Intersection(Vec<Self>),
    Filter { shape: usize, nodes: Box<Self> },
    Function { name: NamedNode, args: Vec<Self> },
}

impl NodeExpression {
    pub fn compile(
        graph: &Dataset,
        node: &Term,
        shapes: &HashMap<Term, usize>,
        functions: &Functions,
    ) -> Result<Self> {
        Self::compile_inner(graph, node, shapes, functions, &mut HashSet::new())
    }

    fn compile_inner(
        graph: &Dataset,
        node: &Term,
        shapes: &HashMap<Term, usize>,
        functions: &Functions,
        stack: &mut HashSet<Term>,
    ) -> Result<Self> {
        if node == &Term::from(iri(SH, "this")) {
            return Ok(Self::This);
        }
        if !matches!(node, Term::BlankNode(_)) {
            return Ok(Self::Constant(node.clone()));
        }
        if !stack.insert(node.clone()) {
            return Err(Error::Invalid("Cyclic SHACL node expression".into()));
        }
        let expression = if let Some(path) = one(graph, node, "path")? {
            Self::Path(Path::compile(graph, &path)?)
        } else if let Some(list) = one(graph, node, "union")? {
            Self::Union(
                rdf_list(graph, &list)?
                    .iter()
                    .map(|n| Self::compile_inner(graph, n, shapes, functions, stack))
                    .collect::<Result<_>>()?,
            )
        } else if let Some(list) = one(graph, node, "intersection")? {
            Self::Intersection(
                rdf_list(graph, &list)?
                    .iter()
                    .map(|n| Self::compile_inner(graph, n, shapes, functions, stack))
                    .collect::<Result<_>>()?,
            )
        } else if let Some(shape) = one(graph, node, "filterShape")? {
            let nodes = one(graph, node, "nodes")?
                .ok_or_else(|| Error::Invalid("sh:filterShape requires sh:nodes".into()))?;
            Self::Filter {
                shape: *shapes
                    .get(&shape)
                    .ok_or_else(|| Error::Invalid("Unknown filter shape".into()))?,
                nodes: Box::new(Self::compile_inner(
                    graph, &nodes, shapes, functions, stack,
                )?),
            }
        } else {
            let calls: Vec<_> = graph
                .quads_for_pattern(
                    Some(subject(node)?.as_ref()),
                    None,
                    None,
                    Some(GraphNameRef::DefaultGraph),
                )
                .filter(|q| functions.contains(&q.predicate.into_owned()))
                .map(|q| (q.predicate.into_owned(), q.object.into_owned()))
                .collect();
            if calls.len() != 1 {
                return Err(Error::Invalid(format!(
                    "Node expression {node} requires exactly one known function or expression operator"
                )));
            }
            let (name, list) = &calls[0];
            Self::Function {
                name: name.clone(),
                args: rdf_list(graph, list)?
                    .iter()
                    .map(|n| Self::compile_inner(graph, n, shapes, functions, stack))
                    .collect::<Result<_>>()?,
            }
        };
        stack.remove(node);
        Ok(expression)
    }

    pub fn evaluate(
        &self,
        focus: &Term,
        data: &Dataset,
        functions: &Functions,
        conforms: &mut impl FnMut(usize, &Term) -> Result<bool>,
    ) -> Result<HashSet<Term>> {
        Ok(match self {
            Self::This => HashSet::from([focus.clone()]),
            Self::Constant(term) => HashSet::from([term.clone()]),
            Self::Path(path) => path.values(data, focus)?.into_iter().collect(),
            Self::Union(expressions) => {
                let mut nodes = HashSet::new();
                for expr in expressions {
                    nodes.extend(expr.evaluate(focus, data, functions, conforms)?);
                }
                nodes
            }
            Self::Intersection(expressions) => {
                let mut result = None::<HashSet<Term>>;
                for expr in expressions {
                    let nodes = expr.evaluate(focus, data, functions, conforms)?;
                    if let Some(result) = &mut result {
                        result.retain(|n| nodes.contains(n));
                    } else {
                        result = Some(nodes);
                    }
                }
                result.unwrap_or_default()
            }
            Self::Filter { shape, nodes } => {
                let mut result = HashSet::new();
                for node in nodes.evaluate(focus, data, functions, conforms)? {
                    if conforms(*shape, &node)? {
                        result.insert(node);
                    }
                }
                result
            }
            Self::Function { name, args } => {
                let mut products = vec![Vec::new()];
                for arg in args {
                    let values = arg.evaluate(focus, data, functions, conforms)?;
                    let mut next = Vec::new();
                    for product in products {
                        for value in &values {
                            let mut p = product.clone();
                            p.push(value.clone());
                            next.push(p);
                        }
                    }
                    products = next;
                }
                let mut result = HashSet::new();
                for product in products {
                    if let Some(value) = functions.call(name, &product, data)? {
                        result.insert(value);
                    }
                }
                result
            }
        })
    }
}

//! Stable RDF descriptions for human-readable reports, independent of blank IDs.

use std::collections::{BTreeMap, HashSet};

use oxigraph::model::*;

use crate::graph::*;
use crate::{GraphRead, Result};

pub(crate) struct Display<'a, G: GraphRead + ?Sized> {
    pub shape_namespaces: Vec<(String, String)>,
    pub data_namespaces: Vec<(String, String)>,
    pub data: &'a G,
    pub shapes: &'a Dataset,
}

impl<G: GraphRead + ?Sized> Display<'_, G> {
    pub fn iri(&self, node: &NamedNode) -> String {
        Self::iri_in(node, &self.shape_namespaces)
    }

    fn iri_in(node: &NamedNode, namespaces: &[(String, String)]) -> String {
        let mut candidates: Vec<_> = namespaces
            .iter()
            .filter_map(|(p, ns)| {
                node.as_str()
                    .strip_prefix(ns)
                    .filter(|local| {
                        !local.is_empty()
                            && local
                                .chars()
                                .all(|c| c.is_alphanumeric() || "_-.:".contains(c))
                    })
                    .map(|local| (ns.len(), format!("{p}:{local}")))
            })
            .collect();
        candidates.sort_by(|(a, x), (b, y)| b.cmp(a).then_with(|| x.cmp(y)));
        candidates
            .into_iter()
            .next()
            .map(|(_, s)| s)
            .unwrap_or_else(|| node.to_string())
    }

    pub fn term(&self, term: &Term, shapes: bool) -> Result<String> {
        if shapes {
            Self::describe(term, self.shapes, &self.shape_namespaces)
        } else {
            Self::describe(term, self.data, &self.data_namespaces)
        }
    }

    fn describe(
        term: &Term,
        graph: &(impl GraphRead + ?Sized),
        namespaces: &[(String, String)],
    ) -> Result<String> {
        let mut context = None;
        if let Term::BlankNode(node) = term {
            // bounded: retain only the best context for this reported blank node.
            for quad in graph.matching_quads(Some(node.as_ref().into()), None, None, None) {
                Self::select_context(&mut context, quad?.graph_name);
            }
            if context.is_none() {
                for quad in graph.matching_quads(None, None, Some(term.as_ref()), None) {
                    Self::select_context(&mut context, quad?.graph_name);
                }
            }
        }
        Self::inner(
            term,
            graph,
            &context.unwrap_or(GraphName::DefaultGraph),
            namespaces,
            &mut HashSet::new(),
        )
    }

    fn select_context(current: &mut Option<GraphName>, candidate: GraphName) {
        let key = |name: &GraphName| {
            (
                matches!(name, GraphName::NamedNode(n) if n.as_str() == "urn:pyshacl:inference"),
                !name.is_default_graph(),
                name.to_string(),
            )
        };
        if current
            .as_ref()
            .is_none_or(|selected| key(&candidate) < key(selected))
        {
            *current = Some(candidate);
        }
    }

    fn inner(
        term: &Term,
        graph: &(impl GraphRead + ?Sized),
        context: &GraphName,
        namespaces: &[(String, String)],
        stack: &mut HashSet<Term>,
    ) -> Result<String> {
        Ok(match term {
            Term::NamedNode(n) => Self::iri_in(n, namespaces),
            Term::Literal(l) => {
                let text = Literal::new_simple_literal(l.value()).to_string();
                if let Some(language) = l.language() {
                    format!("{text}@{language}")
                } else if l.datatype() == iri(XSD, "string").as_ref() {
                    text
                } else {
                    format!(
                        "{text}^^{}",
                        Self::iri_in(&l.datatype().into_owned(), namespaces)
                    )
                }
            }
            Term::BlankNode(_) => {
                if stack.len() >= 20 || !stack.insert(term.clone()) {
                    return Ok("[ ... ]".into());
                }
                let mut properties = BTreeMap::<String, Vec<String>>::new();
                for q in graph.matching_quads(
                    Some(subject(term).expect("blank node").as_ref()),
                    None,
                    None,
                    Some(context.as_ref()),
                ) {
                    let q = q?;
                    properties
                        .entry(Self::iri_in(&q.predicate, namespaces))
                        .or_default()
                        .push(Self::inner(&q.object, graph, context, namespaces, stack)?);
                }
                let mut descriptions = Vec::new();
                for (p, mut values) in properties {
                    values.sort();
                    values.dedup();
                    descriptions.push(format!("{p} {}", values.join(", ")));
                }
                stack.remove(term);
                format!("[ {} ]", descriptions.join(" ; "))
            }
        })
    }
}

//! Stable RDF descriptions for human-readable reports, independent of blank IDs.

use std::collections::{BTreeMap, HashSet};

use oxigraph::model::*;

use crate::graph::*;

pub(crate) struct Display<'a> {
    pub namespaces: Vec<(String, String)>,
    pub data: &'a Dataset,
    pub shapes: &'a Dataset,
}

impl Display<'_> {
    pub fn iri(&self, node: &NamedNode) -> String {
        let mut candidates: Vec<_> = self
            .namespaces
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

    pub fn term(&self, term: &Term, shapes: bool) -> String {
        let graph = if shapes { self.shapes } else { self.data };
        let context = if let Term::BlankNode(node) = term {
            let mut contexts: Vec<_> = graph
                .quads_for_subject(node.as_ref())
                .map(|q| q.graph_name.into_owned())
                .collect();
            if contexts.is_empty() {
                contexts.extend(
                    graph
                        .quads_for_object(term.as_ref())
                        .map(|q| q.graph_name.into_owned()),
                );
            }
            // Prefer source statements to the dedicated inference destination.
            // The evaluator's synthetic union is never used for descriptions.
            contexts.sort_by_key(|name| (
                matches!(name, GraphName::NamedNode(n) if n.as_str() == "urn:pyshacl:inference"),
                !name.is_default_graph(),
                name.to_string(),
            ));
            contexts
                .into_iter()
                .next()
                .unwrap_or(GraphName::DefaultGraph)
        } else {
            GraphName::DefaultGraph
        };
        self.inner(term, graph, &context, &mut HashSet::new())
    }

    fn inner(
        &self,
        term: &Term,
        graph: &Dataset,
        context: &GraphName,
        stack: &mut HashSet<Term>,
    ) -> String {
        match term {
            Term::NamedNode(n) => self.iri(n),
            Term::Literal(l) => {
                let text = Literal::new_simple_literal(l.value()).to_string();
                if let Some(language) = l.language() {
                    format!("{text}@{language}")
                } else if l.datatype() == iri(XSD, "string").as_ref() {
                    text
                } else {
                    format!("{text}^^{}", self.iri(&l.datatype().into_owned()))
                }
            }
            Term::BlankNode(_) => {
                if stack.len() >= 20 || !stack.insert(term.clone()) {
                    return "[ ... ]".into();
                }
                let mut properties = BTreeMap::<String, Vec<String>>::new();
                for q in graph.quads_for_subject(subject(term).expect("blank node").as_ref()) {
                    if q.graph_name != context.as_ref() {
                        continue;
                    }
                    properties
                        .entry(self.iri(&q.predicate.into_owned()))
                        .or_default()
                        .push(self.inner(&q.object.into_owned(), graph, context, stack));
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
        }
    }
}

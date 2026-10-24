//! Stable RDF descriptions for human-readable reports, independent of blank IDs.

use std::collections::{BTreeMap, HashSet};

use bigdecimal::BigDecimal;
use num_bigint::BigInt;
use oxigraph::model::*;

use crate::graph::*;
use crate::{Error, GraphRead, Result};

#[derive(Default)]
struct DescriptionPath {
    active: HashSet<Term>,
    depth: usize,
    cyclic: bool,
}

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
            &mut DescriptionPath::default(),
            false,
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

    fn literal(literal: &Literal, namespaces: &[(String, String)]) -> String {
        // Human-readable pySHACL descriptions contain raw lexical text, rather
        // than N-Triples escapes. RDF serialization keeps its separate formatter.
        let mut value = format!("\"{}\"", literal.value());
        let scalar = match literal.datatype().as_str().strip_prefix(XSD) {
            Some("boolean") => match literal.value() {
                "true" | "1" => Some("True".into()),
                "false" | "0" => Some("False".into()),
                _ => None,
            },
            Some(
                "integer" | "long" | "int" | "short" | "byte" | "unsignedLong" | "unsignedInt"
                | "unsignedShort" | "unsignedByte" | "nonNegativeInteger" | "positiveInteger"
                | "nonPositiveInteger" | "negativeInteger",
            ) => literal
                .value()
                .parse::<BigInt>()
                .ok()
                .map(|value| value.to_string()),
            Some("decimal") => literal
                .value()
                .parse::<BigDecimal>()
                .ok()
                .map(|value| value.to_string()),
            _ => None,
        };
        if let Some(scalar) = scalar.filter(|scalar| scalar != literal.value()) {
            value.push_str(&format!(" = {scalar}"));
        }
        if let Some(language) = literal.language() {
            value.push_str(&format!(", lang={language}"));
        } else if literal.has_explicit_datatype() {
            value.push_str(&format!(
                ", datatype={}",
                Self::iri_in(&literal.datatype().into_owned(), namespaces)
            ));
        }
        format!("Literal({value})")
    }

    fn collection_value(
        graph: &(impl GraphRead + ?Sized),
        node: &Term,
        predicate: &NamedNode,
        context: &GraphName,
    ) -> Result<Term> {
        let mut values = graph.matching_quads(
            Some(subject(node)?.as_ref()),
            Some(predicate.as_ref()),
            None,
            Some(context.as_ref()),
        );
        let first = values.next().transpose()?;
        if first.is_none() || values.next().transpose()?.is_some() {
            return Err(Error::Invalid(format!("Malformed RDF list at {node}")));
        }
        Ok(first.expect("one list value checked above").object)
    }

    fn collection(
        head: &Term,
        graph: &(impl GraphRead + ?Sized),
        context: &GraphName,
        namespaces: &[(String, String)],
        stack: &mut DescriptionPath,
    ) -> Result<String> {
        // pySHACL starts blank descriptions at recursion 1 and adds two per
        // nested blank. Its recursion >= 12 boundary is the seventh frame.
        if stack.active.len() >= 6 {
            return Ok("<http://recursion.too.deep>".into());
        }
        if !stack.active.insert(head.clone()) {
            return Err(Error::Invalid("Cyclic RDF list description".into()));
        }
        stack.depth += 1;
        // bounded: one visited cell per emitted collection item, never source-wide.
        let mut cells = HashSet::new();
        let mut node = head.clone();
        let mut text = String::from("( ");
        while node != Term::from(iri(RDF, "nil")) {
            if !cells.insert(node.clone()) {
                return Err(Error::Invalid(format!("Cyclic RDF list at {node}")));
            }
            let first = Self::collection_value(graph, &node, &iri(RDF, "first"), context)?;
            text.push_str(&Self::inner(
                &first, graph, context, namespaces, stack, true,
            )?);
            text.push(' ');
            node = Self::collection_value(graph, &node, &iri(RDF, "rest"), context)?;
        }
        text.push(')');
        stack.depth -= 1;
        stack.active.remove(head);
        Ok(text)
    }

    fn inner(
        term: &Term,
        graph: &(impl GraphRead + ?Sized),
        context: &GraphName,
        namespaces: &[(String, String)],
        stack: &mut DescriptionPath,
        strict_collection: bool,
    ) -> Result<String> {
        Ok(match term {
            Term::NamedNode(n) => Self::iri_in(n, namespaces),
            Term::Literal(literal) => Self::literal(literal, namespaces),
            Term::BlankNode(_) => {
                let first = graph
                    .matching_quads(
                        Some(subject(term)?.as_ref()),
                        Some(iri(RDF, "first").as_ref()),
                        None,
                        Some(context.as_ref()),
                    )
                    .next()
                    .transpose()?;
                if first.is_some() {
                    return Self::collection(term, graph, context, namespaces, stack);
                }
                if strict_collection && stack.active.len() >= 6 {
                    return Ok("<http://recursion.too.deep>".into());
                }
                let revisited = stack.active.contains(term);
                if strict_collection && revisited {
                    return Err(Error::Invalid("Cyclic RDF list item description".into()));
                }
                // Only active cycles enter this reference rendering budget. Acyclic
                // descriptions retain their existing depth and shared-node behavior.
                if (stack.cyclic || revisited) && stack.depth >= 6 {
                    return Ok("<http://recursion.too.deep>".into());
                }
                if stack.active.len() >= 20 {
                    return Ok("[ ... ]".into());
                }
                let inserted = stack.active.insert(term.clone());
                let previous_cycle = stack.cyclic;
                stack.cyclic |= revisited;
                stack.depth += 1;
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
                        .push(Self::inner(
                            &q.object,
                            graph,
                            context,
                            namespaces,
                            stack,
                            strict_collection,
                        )?);
                }
                let mut descriptions = Vec::new();
                for (p, mut values) in properties {
                    values.sort();
                    values.dedup();
                    descriptions.push(format!("{p} {}", values.join(", ")));
                }
                stack.depth -= 1;
                stack.cyclic = previous_cycle;
                if inserted {
                    stack.active.remove(term);
                }
                if descriptions.is_empty() {
                    return Ok("[ ]".into());
                }
                format!("[ {} ]", descriptions.join(" ; "))
            }
        })
    }
}

#[cfg(test)]
#[path = "display_tests.rs"]
mod tests;

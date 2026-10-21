//! Explicit RDF 1.1 string identity for the upstream Store convenience API.
use oxigraph::model::*;
use oxigraph::store::Transaction;

use crate::graph::store_quad;
use crate::graph_write::GraphWrite;
use crate::{Error, GraphRead, Result};

pub(crate) struct Rdf11Transaction<'read, 'store> {
    inner: &'read mut Transaction<'store>,
}

impl<'read, 'store> Rdf11Transaction<'read, 'store> {
    pub(crate) fn new(inner: &'read mut Transaction<'store>) -> Self {
        Self { inner }
    }
}

impl<'read, 'store> GraphRead for Rdf11Transaction<'read, 'store> {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'read, 'store> {
        // bounded: at most one query term, independent of the source relation.
        let object = object.map(|term| match term {
            TermRef::Literal(literal) if literal.datatype() == oxrdf::vocab::xsd::STRING => {
                Literal::new_simple_literal(literal.value()).into()
            }
            term => term.into_owned(),
        });
        self.inner
            .quads_for_pattern(subject, predicate, object.as_ref().map(Term::as_ref), graph)
            .map(|quad| {
                quad.map(store_quad)
                    .map_err(|error| Error::Runtime(error.to_string()))
            })
    }

    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_ {
        self.inner
            .named_graphs()
            .map(|graph| graph.map_err(|error| Error::Runtime(error.to_string())))
    }

    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool> {
        self.inner
            .contains_named_graph(graph.as_ref())
            .map_err(|error| Error::Runtime(error.to_string()))
    }
}

impl GraphWrite for Rdf11Transaction<'_, '_> {
    fn insert_quad(&mut self, quad: QuadRef<'_>) -> Result<bool> {
        self.inner.insert_quad(quad)
    }
}

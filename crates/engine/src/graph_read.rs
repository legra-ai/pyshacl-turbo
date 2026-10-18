//! Borrowed indexed reads shared by dataset and transaction-backed traversal.
use oxigraph::model::*;
use oxigraph::store::Transaction;

use crate::{Error, Result};

/// A fallible stream of stored quads, with explicit graph matching.
///
/// `None` matches every graph; `Some(DefaultGraph)` matches only the default
/// graph. Implementations preserve stored RDF terms and graph contexts. This
/// interface neither constructs a graph union nor copies the base dataset.
/// Storage owners remain responsible for exact-term encoding: a reader cannot
/// recover lexical forms already normalized by its storage backend.
/// During a consistent read, identical patterns must yield the same first quad;
/// no lexical sorting is required. Borrowed views use this stable representative
/// to deduplicate graph contexts without retaining all previously visited triples.
pub trait GraphRead {
    /// Stream matching quads. Read failures must remain errors, never omissions.
    /// Retain the source borrow, not the caller's temporary pattern references.
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, Self>;

    /// Stream each named graph exactly once, including empty backend graphs.
    /// Iteration must not materialize the set of graph names.
    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_;

    /// Test graph existence, including empty graphs in capable storage backends.
    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool>;
}

impl GraphRead for Dataset {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a> {
        // bounded: at most four owned pattern terms, independent of source size.
        let predicate = predicate.map(NamedNodeRef::into_owned);
        let object = object.map(TermRef::into_owned);
        let graph = graph.map(GraphNameRef::into_owned);
        let candidates: Box<dyn Iterator<Item = QuadRef<'a>> + 'a> = if let Some(subject) = subject
        {
            Box::new(self.quads_for_subject(subject))
        } else if let Some(object) = object.as_ref() {
            Box::new(self.quads_for_object(object.as_ref()))
        } else if let Some(predicate) = predicate.as_ref() {
            Box::new(self.quads_for_predicate(predicate.as_ref()))
        } else if let Some(graph) = graph.as_ref() {
            Box::new(self.quads_for_graph_name(graph.as_ref()))
        } else {
            Box::new(self.iter())
        };
        candidates
            .filter(move |q| {
                predicate.as_ref().is_none_or(|p| p.as_ref() == q.predicate)
                    && object.as_ref().is_none_or(|o| o.as_ref() == q.object)
                    && graph.as_ref().is_none_or(|g| g.as_ref() == q.graph_name)
            })
            .map(|quad| Ok(quad.into_owned()))
    }

    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_ {
        // Select one indexed representative per graph; retain no graph-name set.
        self.iter().filter_map(|quad| {
            let name = match quad.graph_name {
                GraphNameRef::NamedNode(node) => NamedOrBlankNode::from(node.into_owned()),
                GraphNameRef::BlankNode(node) => NamedOrBlankNode::from(node.into_owned()),
                GraphNameRef::DefaultGraph => return None,
            };
            (self.quads_for_graph_name(quad.graph_name).next() == Some(quad)).then_some(Ok(name))
        })
    }
    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool> {
        Ok(self.quads_for_graph_name(graph.as_ref()).next().is_some())
    }
}

impl<'tx> GraphRead for Transaction<'tx> {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'tx> {
        self.quads_for_pattern(subject, predicate, object, graph)
            .map(|quad| {
                quad.map_err(|error| Error::Runtime(format!("Storage read failed: {error}")))
            })
    }

    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_ {
        Transaction::named_graphs(self).map(|graph| {
            graph.map_err(|error| Error::Runtime(format!("Storage read failed: {error}")))
        })
    }

    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool> {
        Transaction::contains_named_graph(self, graph.as_ref())
            .map_err(|error| Error::Runtime(format!("Storage read failed: {error}")))
    }
}

//! Borrowed logical dataset views; neither view materializes the base relation.
use oxigraph::model::*;

use crate::{Error, GraphRead, Result};

type Matches<'a> = Box<dyn Iterator<Item = Result<Quad>> + 'a>;

/// Expose the union as the default graph while preserving original named graphs.
/// The source must remain consistent throughout a read, as a borrowed Dataset
/// or native transaction does. A repeated exact match must select the same
/// first quad; no sorted order is required.
pub struct UnionGraph<'a, G: GraphRead + ?Sized> {
    source: &'a G,
}

impl<'a, G: GraphRead + ?Sized> UnionGraph<'a, G> {
    /// Borrow a consistent source; do not clone or snapshot its base data.
    pub fn new(source: &'a G) -> Self {
        Self { source }
    }

    fn default_matches<'b>(
        &'b self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'b, G> {
        self.source
            .matching_quads(subject, predicate, object, None)
            .filter_map(|quad| match quad {
                Err(error) => Some(Err(error)),
                Ok(mut quad) => match self.representative(&quad) {
                    Err(error) => Some(Err(error)),
                    Ok(false) => None,
                    Ok(true) => {
                        quad.graph_name = GraphName::DefaultGraph;
                        Some(Ok(quad))
                    }
                },
            })
    }

    fn representative(&self, quad: &Quad) -> Result<bool> {
        // An exact indexed lookup identifies one context without retaining a
        // dataset-sized visited set. Memory storage need not yield sorted quads.
        let first = self
            .source
            .matching_quads(
                Some(quad.subject.as_ref()),
                Some(quad.predicate.as_ref()),
                Some(quad.object.as_ref()),
                None,
            )
            .next()
            .transpose()?
            .ok_or_else(|| Error::Runtime("Graph changed during union read".into()))?;
        Ok(first.graph_name == quad.graph_name)
    }
}

impl<'source, G: GraphRead + ?Sized> GraphRead for UnionGraph<'source, G> {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'source, G> {
        let matches: Matches<'a> = match graph {
            Some(GraphNameRef::DefaultGraph) => {
                Box::new(self.default_matches(subject, predicate, object))
            }
            Some(_) => Box::new(
                self.source
                    .matching_quads(subject, predicate, object, graph),
            ),
            None => Box::new(
                self.default_matches(subject, predicate, object).chain(
                    self.source
                        .matching_quads(subject, predicate, object, None)
                        .filter(|q| match q {
                            Ok(q) => !q.graph_name.is_default_graph(),
                            Err(_) => true,
                        }),
                ),
            ),
        };
        matches
    }

    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_ {
        self.source.named_graphs()
    }

    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool> {
        self.source.contains_named_graph(graph)
    }
}

/// Add a separate named shapes graph without cloning or modifying the base.
/// Shapes are projected from their union; their original contexts do not leak
/// into the base dataset. The reserved graph exists even when shapes are empty.
pub struct OverlayGraph<'a, G: GraphRead + ?Sized, S: GraphRead + ?Sized> {
    source: &'a G,
    shapes: UnionGraph<'a, S>,
    graph: GraphName,
}

impl<'a, G: GraphRead + ?Sized, S: GraphRead + ?Sized> OverlayGraph<'a, G, S> {
    /// Reserve a fresh named graph; collisions, including empty graphs, fail.
    pub fn new(source: &'a G, shapes: &'a S, graph: NamedOrBlankNode) -> Result<Self> {
        if source.contains_named_graph(&graph)? {
            return Err(Error::Invalid(format!(
                "Overlay graph already exists: {graph}"
            )));
        }
        Ok(Self {
            source,
            shapes: UnionGraph::new(shapes),
            graph: graph.into(),
        })
    }

    fn overlay_matches<'b>(
        &'b self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'b, G, S> {
        self.shapes
            .matching_quads(subject, predicate, object, Some(GraphNameRef::DefaultGraph))
            .map(|quad| {
                quad.map(|mut quad| {
                    quad.graph_name = self.graph.clone();
                    quad
                })
            })
    }
}

impl<'source, G: GraphRead + ?Sized, S: GraphRead + ?Sized> GraphRead
    for OverlayGraph<'source, G, S>
{
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'source, G, S> {
        let matches: Matches<'a> = match graph {
            Some(graph) if graph == self.graph.as_ref() => {
                Box::new(self.overlay_matches(subject, predicate, object))
            }
            Some(_) => Box::new(
                self.source
                    .matching_quads(subject, predicate, object, graph),
            ),
            None => Box::new(
                self.source
                    .matching_quads(subject, predicate, object, None)
                    .chain(self.overlay_matches(subject, predicate, object)),
            ),
        };
        matches
    }

    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_ {
        self.source
            .named_graphs()
            .chain(std::iter::once(Ok(match &self.graph {
                GraphName::NamedNode(node) => node.clone().into(),
                GraphName::BlankNode(node) => node.clone().into(),
                GraphName::DefaultGraph => unreachable!("overlay reserves a named graph"),
            })))
    }

    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool> {
        Ok(self.graph.as_ref() == GraphNameRef::from(graph.as_ref())
            || self.source.contains_named_graph(graph)?)
    }
}

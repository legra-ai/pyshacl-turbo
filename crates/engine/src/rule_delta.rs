//! Private rule additions over a borrowed source; never copy the base relation.
use crate::graph_write::GraphWrite;
use crate::{Error, GraphRead, Result};
use oxigraph::model::*;

pub(crate) struct RuleDelta<'a, G: GraphRead + ?Sized> {
    source: &'a G,
    additions: Dataset,
}

impl<'a, G: GraphRead + ?Sized> RuleDelta<'a, G> {
    pub fn new(source: &'a G) -> Self {
        Self {
            source,
            additions: Dataset::new(),
        }
    }
}

impl<G: GraphRead + ?Sized> GraphWrite for RuleDelta<'_, G> {
    fn insert_quad(&mut self, quad: QuadRef<'_>) -> Result<bool> {
        if !quad.graph_name.is_default_graph() {
            return Err(Error::Invalid(
                "Rule additions must use the default graph".into(),
            ));
        }
        if self
            .source
            .matching_quads(
                Some(quad.subject),
                Some(quad.predicate),
                Some(quad.object),
                Some(quad.graph_name),
            )
            .next()
            .transpose()?
            .is_some()
        {
            return Ok(false);
        }
        Ok(self.additions.insert(quad))
    }
}

impl<'source, G: GraphRead + ?Sized> GraphRead for RuleDelta<'source, G> {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'_>>,
        predicate: Option<NamedNodeRef<'_>>,
        object: Option<TermRef<'_>>,
        graph: Option<GraphNameRef<'_>>,
    ) -> impl Iterator<Item = Result<Quad>> + use<'a, 'source, G> {
        self.source
            .matching_quads(subject, predicate, object, graph)
            .chain(
                self.additions
                    .matching_quads(subject, predicate, object, graph),
            )
    }

    fn named_graphs(&self) -> impl Iterator<Item = Result<NamedOrBlankNode>> + '_ {
        self.source.named_graphs()
    }

    fn contains_named_graph(&self, graph: &NamedOrBlankNode) -> Result<bool> {
        self.source.contains_named_graph(graph)
    }
}

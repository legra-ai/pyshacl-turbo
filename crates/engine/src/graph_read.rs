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
pub trait GraphRead {
    /// Stream matching quads. Read failures must remain errors, never omissions.
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'a>>,
        predicate: Option<NamedNodeRef<'a>>,
        object: Option<TermRef<'a>>,
        graph: Option<GraphNameRef<'a>>,
    ) -> impl Iterator<Item = Result<Quad>> + 'a;
}

impl GraphRead for Dataset {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'a>>,
        predicate: Option<NamedNodeRef<'a>>,
        object: Option<TermRef<'a>>,
        graph: Option<GraphNameRef<'a>>,
    ) -> impl Iterator<Item = Result<Quad>> + 'a {
        self.quads_for_pattern(subject, predicate, object, graph)
            .map(|quad| Ok(quad.into_owned()))
    }
}

impl GraphRead for Transaction<'_> {
    fn matching_quads<'a>(
        &'a self,
        subject: Option<NamedOrBlankNodeRef<'a>>,
        predicate: Option<NamedNodeRef<'a>>,
        object: Option<TermRef<'a>>,
        graph: Option<GraphNameRef<'a>>,
    ) -> impl Iterator<Item = Result<Quad>> + 'a {
        self.quads_for_pattern(subject, predicate, object, graph)
            .map(|quad| {
                quad.map_err(|error| Error::Runtime(format!("Storage read failed: {error}")))
            })
    }
}

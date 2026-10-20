//! Compact exact compilation keys built from typed RDF input.

use pyo3::prelude::*;

use crate::terms::{Batch, DecodedTerms};

#[pyfunction]
pub(crate) fn canonical_shapes(py: Python<'_>, source: &Bound<'_, PyAny>) -> PyResult<String> {
    let input: Batch = source.extract()?;
    py.detach(|| {
        let mut lines = DecodedTerms::new(input)?
            .map(|quad| {
                let quad = quad?;
                Ok(format!(
                    "{} {} {} .\n",
                    quad.subject, quad.predicate, quad.object
                ))
            })
            .collect::<pyshacl_turbo_engine::Result<Vec<_>>>()?;
        lines.sort_unstable();
        lines.dedup();
        Ok(lines.concat())
    })
    .map_err(crate::error)
}

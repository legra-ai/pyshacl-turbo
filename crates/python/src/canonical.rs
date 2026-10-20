//! Compact exact compilation keys built from typed RDF input.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;

use crate::terms::{Batch, DecodedTerms};

pub(crate) const BATCH_SIZE: usize = 256;

#[pyfunction]
pub(crate) fn canonical_shapes(py: Python<'_>, source: &Bound<'_, PyAny>) -> PyResult<String> {
    let mut lines = Vec::new();
    for batch in source.try_iter()? {
        let batch = batch?;
        if batch.get_item(0)?.len()? > 4 * BATCH_SIZE || batch.get_item(1)?.len()? > BATCH_SIZE {
            return Err(PyValueError::new_err(
                "Shape transfer batches may contain at most 256 triples",
            ));
        }
        let input: Batch = batch.extract()?;
        let output = py
            .detach(|| {
                DecodedTerms::new(input)?
                    .map(|quad| {
                        let quad = quad?;
                        Ok(format!(
                            "{} {} {} .\n",
                            quad.subject, quad.predicate, quad.object
                        ))
                    })
                    .collect::<pyshacl_turbo_engine::Result<Vec<_>>>()
            })
            .map_err(crate::error)?;
        lines.extend(output);
    }
    Ok(py.detach(|| {
        lines.sort_unstable();
        lines.dedup();
        lines.concat()
    }))
}

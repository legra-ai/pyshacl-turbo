//! Compact exact compilation keys built from typed RDF input.

use pyo3::prelude::*;

use crate::terms::Input;

#[pyfunction]
pub(crate) fn canonical_shapes(py: Python<'_>, source: &Bound<'_, PyAny>) -> PyResult<String> {
    let input = Input::read(source, "terms", None)?;
    py.detach(|| {
        let data = input.parse()?;
        let mut lines: Vec<_> = data
            .iter()
            .map(|quad| format!("{} {} {} .\n", quad.subject, quad.predicate, quad.object))
            .collect();
        lines.sort_unstable();
        lines.dedup();
        Ok(lines.concat())
    })
    .map_err(crate::error)
}

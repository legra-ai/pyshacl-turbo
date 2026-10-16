mod terms;

use pyo3::exceptions::{PyNotImplementedError, PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use pyshacl_turbo_engine::oxigraph::io::RdfFormat;
use pyshacl_turbo_engine::oxigraph::{
    io::{RdfParser, RdfSerializer},
    model::*,
};
use pyshacl_turbo_engine::{
    CompiledShapes, Error, Options, parse_dataset, parse_graph, serialize_graph,
};

pyo3::create_exception!(_native, ValidationFailure, PyValueError);

fn error(error: Error) -> PyErr {
    match error {
        Error::ValidationFailure(_) => ValidationFailure::new_err(error.to_string()),
        Error::Unsupported(_) => PyNotImplementedError::new_err(error.to_string()),
        Error::Invalid(_) => PyValueError::new_err(error.to_string()),
        _ => PyRuntimeError::new_err(error.to_string()),
    }
}

struct InputFormat {
    rdf: RdfFormat,
    store_strings: bool,
}

impl InputFormat {
    fn parse(&self, source: &str, base: Option<&str>) -> pyshacl_turbo_engine::Result<Dataset> {
        if self.store_strings {
            pyshacl_turbo_engine::parse_store_snapshot(source)
        } else {
            parse_dataset(source, self.rdf, base)
        }
    }
}

fn format(name: &str) -> PyResult<InputFormat> {
    let rdf = match name {
        "turtle" | "ttl" => Ok(RdfFormat::Turtle),
        "nt" | "ntriples" => Ok(RdfFormat::NTriples),
        "nquads" | "nq" | "oxigraph-nquads" => Ok(RdfFormat::NQuads),
        "trig" => Ok(RdfFormat::TriG),
        "xml" | "rdfxml" => Ok(RdfFormat::RdfXml),
        "n3" => Ok(RdfFormat::N3),
        "json-ld" | "jsonld" => Ok(RdfFormat::JsonLd {
            profile: Default::default(),
        }),
        _ => Err(PyNotImplementedError::new_err(format!(
            "Unsupported RDF format: {name}"
        ))),
    }?;
    Ok(InputFormat {
        rdf,
        store_strings: name == "oxigraph-nquads",
    })
}

#[pyfunction]
fn parse_rdf(
    py: Python<'_>,
    source: &str,
    rdf_format: &str,
    base: Option<&str>,
) -> PyResult<(String, Vec<(String, String)>)> {
    let format = format(rdf_format)?;
    py.detach(|| {
        let mut parser = RdfParser::from_format(format.rdf);
        if let Some(base) = base {
            parser = parser
                .with_base_iri(base)
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
        }
        let mut parser = parser.for_slice(source.as_bytes());
        let mut writer = RdfSerializer::from_format(RdfFormat::NQuads).for_writer(Vec::new());
        for quad in parser.by_ref() {
            let quad = quad.map_err(|e| PyValueError::new_err(e.to_string()))?;
            let quad = if format.store_strings {
                pyshacl_turbo_engine::store_quad(quad)
            } else {
                quad
            };
            writer
                .serialize_quad(&quad)
                .map_err(|e| PyValueError::new_err(e.to_string()))?;
        }
        let prefixes = parser
            .prefixes()
            .map(|(p, n)| (p.to_owned(), n.to_owned()))
            .collect();
        let output = writer
            .finish()
            .map_err(|e| PyValueError::new_err(e.to_string()))?;
        Ok((
            String::from_utf8(output).map_err(|e| PyValueError::new_err(e.to_string()))?,
            prefixes,
        ))
    })
}

#[pyfunction]
fn additions(
    py: Python<'_>,
    before: &Bound<'_, PyAny>,
    rdf_format: &str,
    after: &Bound<'_, PyAny>,
) -> PyResult<Py<PyAny>> {
    let direct = !after.is_instance_of::<pyo3::types::PyString>();
    let before = terms::Input::read(before, rdf_format, None)?;
    let after = terms::Input::read(after, if direct { "terms" } else { "nquads" }, None)?;
    let output = py
        .detach(|| {
            let before = before.parse()?;
            let after = after.parse()?;
            let additions = after
                .iter()
                .filter(|q| !before.contains(*q))
                .map(|q| q.into_owned())
                .collect();
            terms::Output::graph(&additions, direct)
        })
        .map_err(error)?;
    output.into_python(py)
}

#[pyfunction]
#[pyo3(signature = (source, rdf_format, mode, destination=None))]
fn infer(
    py: Python<'_>,
    source: &str,
    rdf_format: &str,
    mode: &str,
    destination: Option<&str>,
) -> PyResult<String> {
    let rdf_format = format(rdf_format)?;
    let destination = destination
        .map(NamedNode::new)
        .transpose()
        .map_err(|e| PyValueError::new_err(e.to_string()))?;
    py.detach(|| {
        let mut data = rdf_format.parse(source, None)?;
        if let Some(destination) = destination {
            pyshacl_turbo_engine::infer_into(&mut data, mode, destination.into())?;
        } else {
            pyshacl_turbo_engine::infer(&mut data, mode)?;
        }
        serialize_graph(&data)
    })
    .map_err(error)
}

#[pyfunction]
fn inoculate(py: Python<'_>, source: &str, rdf_format: &str, ontology: &str) -> PyResult<String> {
    let rdf_format = format(rdf_format)?;
    py.detach(|| {
        let mut data = rdf_format.parse(source, None)?;
        let ontology = parse_graph(ontology, RdfFormat::NTriples, None)?;
        pyshacl_turbo_engine::inoculate(&mut data, &ontology);
        serialize_graph(&data)
    })
    .map_err(error)
}

#[pyfunction]
fn query(py: Python<'_>, source: &str, rdf_format: &str, query: &str) -> PyResult<String> {
    use pyshacl_turbo_engine::oxigraph::sparql::QueryResults;
    use serde_json::json;
    let rdf_format = format(rdf_format)?;
    py.detach(|| {
        let mut data = rdf_format.parse(source, None)?;
        let default: Vec<_> = data
            .iter()
            .map(|q| Quad::new(q.subject, q.predicate, q.object, GraphName::DefaultGraph))
            .collect();
        data.extend(default);
        let result = match pyshacl_turbo_engine::evaluate_query(&data, &data, query, &[])? {
            QueryResults::Solutions(solutions) => {
                let variables: Vec<_> = solutions
                    .variables()
                    .iter()
                    .map(|v| v.as_str().to_owned())
                    .collect();
                let mut rows = Vec::new();
                for solution in solutions {
                    let row: serde_json::Map<_, _> = solution?
                        .iter()
                        .map(|(variable, value)| {
                            (variable.as_str().to_owned(), query_result_term(value))
                        })
                        .collect();
                    rows.push(row);
                }
                json!({"head": {"vars": variables}, "results": {"bindings": rows}})
            }
            QueryResults::Boolean(value) => json!({"head": {}, "boolean": value}),
            QueryResults::Graph(_) => {
                return Err(Error::Invalid("SELECT or ASK query required".into()));
            }
        };
        Ok(result.to_string())
    })
    .map_err(error)
}

fn query_result_term(term: &Term) -> serde_json::Value {
    use serde_json::json;
    match term {
        Term::NamedNode(value) => json!({"type": "uri", "value": value.as_str()}),
        Term::BlankNode(value) => json!({"type": "bnode", "value": value.as_str()}),
        Term::Literal(value) => {
            let mut result = json!({"type": "literal", "value": value.value()});
            if let Some(language) = value.language() {
                result["xml:lang"] = json!(language);
            } else if value.has_explicit_datatype() {
                // The standard Oxigraph JSON writer omits xsd:string, losing
                // the explicit datatype required by RDFLib term identity.
                result["datatype"] = json!(value.datatype().as_str());
            }
            result
        }
    }
}

#[pyclass(frozen, name = "CompiledShapes")]
struct PyCompiledShapes {
    inner: CompiledShapes,
}

/// Immutable data snapshot with a precomputed default-union view.
#[pyclass(frozen, name = "TargetData")]
struct PyTargetData {
    inner: Dataset,
}

#[pymethods]
impl PyTargetData {
    #[new]
    fn new(py: Python<'_>, source: &str, rdf_format: &str, base: Option<&str>) -> PyResult<Self> {
        let rdf_format = format(rdf_format)?;
        py.detach(|| {
            let mut data = rdf_format.parse(source, base)?;
            let default: Vec<_> = data
                .iter()
                .filter(|quad| !quad.graph_name.is_default_graph())
                .map(|quad| {
                    Quad::new(
                        quad.subject,
                        quad.predicate,
                        quad.object,
                        GraphName::DefaultGraph,
                    )
                })
                .collect();
            data.extend(default);
            Ok(Self { inner: data })
        })
        .map_err(error)
    }
}

type ReportOutput = (bool, Py<PyAny>, String, Option<Py<PyAny>>, Vec<String>);

#[pymethods]
impl PyCompiledShapes {
    #[new]
    fn new(
        py: Python<'_>,
        source: &str,
        rdf_format: &str,
        base: Option<&str>,
        advanced: bool,
        numeric_booleans: bool,
        namespaces: Vec<(String, String)>,
    ) -> PyResult<Self> {
        let rdf_format = format(rdf_format)?;
        py.detach(|| {
            let graph = parse_graph(source, rdf_format.rdf, base)?;
            Ok(Self {
                inner: CompiledShapes::compile_with_namespaces(
                    graph,
                    advanced,
                    numeric_booleans,
                    &namespaces,
                )?,
            })
        })
        .map_err(error)
    }

    fn shape_nodes(&self) -> Vec<String> {
        self.inner.shape_nodes().map(ToString::to_string).collect()
    }

    fn targeting_index(
        &self,
        py: Python<'_>,
        data: &PyTargetData,
        skip: Vec<String>,
    ) -> PyResult<String> {
        py.detach(|| {
            let skip: std::collections::HashSet<_> = skip.into_iter().collect();
            let skipped = self
                .inner
                .shape_nodes()
                .filter(|node| skip.contains(&node.to_string()))
                .cloned()
                .collect();
            let index = self.inner.targeting_index(&data.inner, &skipped)?;
            let mut output = Dataset::new();
            for (focus, shapes) in index {
                for shape in shapes {
                    let subject = match shape {
                        Term::NamedNode(node) => NamedOrBlankNode::from(node),
                        Term::BlankNode(node) => NamedOrBlankNode::from(node),
                        _ => {
                            return Err(Error::Invalid(
                                "Shape identifier must be an IRI or blank node".into(),
                            ));
                        }
                    };
                    output.insert(&Quad::new(
                        subject,
                        NamedNode::new_unchecked("urn:pyshacl-turbo:target"),
                        focus.clone(),
                        GraphName::DefaultGraph,
                    ));
                }
            }
            serialize_graph(&output)
        })
        .map_err(error)
    }

    fn focus_nodes(
        &self,
        py: Python<'_>,
        node: &str,
        data: &PyTargetData,
        advanced: bool,
    ) -> PyResult<String> {
        py.detach(|| {
            let nodes = self.inner.shape_focus_nodes(node, &data.inner, advanced)?;
            let mut output = Dataset::new();
            for node in nodes {
                output.insert(&Quad::new(
                    NamedNode::new_unchecked("urn:pyshacl-turbo:inspection"),
                    NamedNode::new_unchecked("urn:pyshacl-turbo:focus"),
                    node,
                    GraphName::DefaultGraph,
                ));
            }
            serialize_graph(&output)
        })
        .map_err(error)
    }

    #[allow(clippy::too_many_arguments)]
    fn validate(
        &self,
        py: Python<'_>,
        source: &Bound<'_, PyAny>,
        rdf_format: &str,
        base: Option<&str>,
        iterate_rules: bool,
        max_rule_iterations: usize,
        max_validation_depth: usize,
        include_data: bool,
        allow_infos: bool,
        allow_warnings: bool,
        abort_on_first: bool,
        focus_nodes: Vec<String>,
        use_shapes: Vec<String>,
        namespaces: Vec<(String, String)>,
    ) -> PyResult<ReportOutput> {
        let direct = rdf_format == "terms";
        let input = terms::Input::read(source, rdf_format, base)?;
        let (conforms, report, text, expanded, warnings) = py
            .detach(|| {
                let mut data = input.parse()?;
                let report = self.inner.validate(
                    &mut data,
                    Options {
                        iterate_rules,
                        max_rule_iterations,
                        max_validation_depth,
                        allow_infos,
                        allow_warnings,
                        abort_on_first,
                        namespaces,
                        focus_nodes: focus_nodes
                            .into_iter()
                            .map(|s| NamedNode::new(s).map(Term::from))
                            .collect::<std::result::Result<_, _>>()
                            .map_err(|e| Error::Invalid(e.to_string()))?,
                        use_shapes: use_shapes
                            .into_iter()
                            .map(|s| NamedNode::new(s).map(Term::from))
                            .collect::<std::result::Result<_, _>>()
                            .map_err(|e| Error::Invalid(e.to_string()))?,
                    },
                )?;
                Ok((
                    report.conforms,
                    terms::Output::graph(&report.graph, direct)?,
                    report.text,
                    if include_data {
                        Some(terms::Output::graph(&data, direct)?)
                    } else {
                        None
                    },
                    report.recursion_warnings,
                ))
            })
            .map_err(error)?;
        Ok((
            conforms,
            report.into_python(py)?,
            text,
            expanded.map(|value| value.into_python(py)).transpose()?,
            warnings,
        ))
    }

    #[allow(clippy::too_many_arguments)]
    fn expand(
        &self,
        py: Python<'_>,
        source: &Bound<'_, PyAny>,
        rdf_format: &str,
        base: Option<&str>,
        iterate_rules: bool,
        max_rule_iterations: usize,
        max_validation_depth: usize,
        focus_nodes: Vec<String>,
        use_shapes: Vec<String>,
        additions_only: bool,
    ) -> PyResult<(Py<PyAny>, Vec<String>)> {
        let direct = rdf_format == "terms";
        let input = terms::Input::read(source, rdf_format, base)?;
        let (output, warnings) = py
            .detach(|| {
                let mut data = input.parse()?;
                let options = Options {
                    iterate_rules,
                    max_rule_iterations,
                    max_validation_depth,
                    focus_nodes: focus_nodes
                        .into_iter()
                        .map(|s| NamedNode::new(s).map(Term::from))
                        .collect::<std::result::Result<_, _>>()
                        .map_err(|e| Error::Invalid(e.to_string()))?,
                    use_shapes: use_shapes
                        .into_iter()
                        .map(|s| NamedNode::new(s).map(Term::from))
                        .collect::<std::result::Result<_, _>>()
                        .map_err(|e| Error::Invalid(e.to_string()))?,
                    ..Options::default()
                };
                if additions_only {
                    let delta = self.inner.expand_rules_delta(&mut data, options)?;
                    Ok((
                        terms::Output::graph(&delta.graph, direct)?,
                        delta.recursion_warnings,
                    ))
                } else {
                    let warnings = self.inner.expand_rules(&mut data, options)?;
                    Ok((terms::Output::graph(&data, direct)?, warnings))
                }
            })
            .map_err(error)?;
        Ok((output.into_python(py)?, warnings))
    }
}

#[pymodule]
fn _native(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PyCompiledShapes>()?;
    module.add_class::<PyTargetData>()?;
    module.add_function(wrap_pyfunction!(parse_rdf, module)?)?;
    module.add_function(wrap_pyfunction!(additions, module)?)?;
    module.add_function(wrap_pyfunction!(infer, module)?)?;
    module.add_function(wrap_pyfunction!(inoculate, module)?)?;
    module.add_function(wrap_pyfunction!(query, module)?)?;
    module.add(
        "ValidationFailure",
        module.py().get_type::<ValidationFailure>(),
    )?;
    Ok(())
}

use std::collections::HashSet;

use oxigraph::model::*;

use crate::constraints::{Constraint, named};
use crate::graph::*;
use crate::path::Path;
use crate::{Error, Result};

pub(crate) struct Parameter {
    pub node: Term,
    pub path: NamedNode,
    variable: Variable,
    optional: bool,
}

pub(crate) struct Component {
    pub node: NamedNode,
    pub parameters: Vec<Parameter>,
    pub validators: Vec<Term>,
    node_validator: Option<Term>,
    property_validator: Option<Term>,
    validator: Option<Term>,
}

impl Component {
    pub fn discover(graph: &Dataset) -> Result<Vec<Self>> {
        let mut result = Vec::new();
        for node in instances(graph, &iri(SH, "ConstraintComponent").into())? {
            // Built-in declarations are vocabulary metadata. Their constraints
            // are compiled by the native Core/AF implementation, not registered
            // a second time as custom components requiring a SPARQL validator.
            const BUILTIN: &[&str] = &[
                "AndConstraintComponent",
                "ClassConstraintComponent",
                "ClosedConstraintComponent",
                "DatatypeConstraintComponent",
                "DisjointConstraintComponent",
                "EqualsConstraintComponent",
                "ExpressionConstraintComponent",
                "HasValueConstraintComponent",
                "InConstraintComponent",
                "LanguageInConstraintComponent",
                "LessThanConstraintComponent",
                "LessThanOrEqualsConstraintComponent",
                "MaxCountConstraintComponent",
                "MaxExclusiveConstraintComponent",
                "MaxInclusiveConstraintComponent",
                "MaxLengthConstraintComponent",
                "MinCountConstraintComponent",
                "MinExclusiveConstraintComponent",
                "MinInclusiveConstraintComponent",
                "MinLengthConstraintComponent",
                "NodeConstraintComponent",
                "NodeKindConstraintComponent",
                "NotConstraintComponent",
                "OrConstraintComponent",
                "PatternConstraintComponent",
                "PropertyConstraintComponent",
                "QualifiedMaxCountConstraintComponent",
                "QualifiedMinCountConstraintComponent",
                "QualifiedValueShapeConstraintComponent",
                "SPARQLConstraintComponent",
                "UniqueLangConstraintComponent",
                "XoneConstraintComponent",
                "sourceConstraintComponent",
            ];
            if matches!(&node, Term::NamedNode(n) if n.as_str().strip_prefix(SH).is_some_and(|name| BUILTIN.contains(&name)))
            {
                continue;
            }
            let mut parameters = Vec::new();
            let mut names = HashSet::new();
            for parameter in values(graph, &node, "parameter")? {
                let path = named(
                    one(graph, &parameter, "path")?
                        .ok_or_else(|| Error::Invalid("Parameter needs sh:path".into()))?,
                    "Parameter sh:path",
                )?;
                let name = path.as_str().rsplit(['#', '/']).next().unwrap_or("");
                let variable = Variable::new(name)
                    .map_err(|e| Error::Invalid(format!("Invalid parameter name: {e}")))?;
                if [
                    "this",
                    "value",
                    "path",
                    "PATH",
                    "currentShape",
                    "shapesGraph",
                ]
                .contains(&name)
                    || !names.insert(variable.clone())
                {
                    return Err(Error::Invalid(format!(
                        "Invalid or duplicate parameter name {name}"
                    )));
                }
                parameters.push(Parameter {
                    path,
                    variable,
                    optional: boolean(graph, &parameter, "optional")?,
                    node: parameter,
                });
            }
            if parameters.is_empty() || parameters.iter().all(|p| p.optional) {
                return Err(Error::Invalid(
                    "Constraint component needs a required parameter".into(),
                ));
            }
            let node_validator = one(graph, &node, "nodeValidator")?;
            let property_validator = one(graph, &node, "propertyValidator")?;
            let validator = one(graph, &node, "validator")?;
            let validators = [&node_validator, &property_validator, &validator]
                .into_iter()
                .flatten()
                .cloned()
                .collect();
            result.push(Self {
                node: named(node, "Constraint component")?,
                parameters,
                validators,
                node_validator,
                property_validator,
                validator,
            });
        }
        Ok(result)
    }

    pub fn compile(
        &self,
        graph: &Dataset,
        shape: &Term,
        path: Option<&Path>,
        namespaces: &[(String, String)],
    ) -> Result<Vec<Constraint>> {
        let mut combinations = vec![Vec::new()];
        for parameter in &self.parameters {
            let values = objects(graph, shape, &parameter.path)?;
            if values.is_empty() {
                if parameter.optional {
                    continue;
                }
                return Ok(Vec::new());
            }
            let mut next = Vec::new();
            for combination in combinations {
                for value in &values {
                    let mut bindings = combination.clone();
                    bindings.push((parameter.variable.clone(), value.clone()));
                    next.push(bindings);
                }
            }
            combinations = next;
        }
        let select_validator = if path.is_some() {
            self.property_validator.as_ref()
        } else {
            self.node_validator.as_ref()
        };
        let (validator, ask) = if let Some(validator) = select_validator {
            (validator, false)
        } else if let Some(validator) = &self.validator {
            (validator, true)
        } else {
            return Err(Error::Unsupported(format!(
                "No applicable validator for {}",
                self.node
            )));
        };
        combinations
            .iter()
            .map(|bindings| {
                crate::sparql::compile_validator(
                    graph,
                    validator,
                    path,
                    bindings,
                    ask,
                    Some(self.node.clone()),
                    namespaces,
                )
                .map(|query| Constraint::Sparql(Box::new(query)))
            })
            .collect()
    }
}

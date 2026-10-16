use std::collections::{HashMap, HashSet, VecDeque};

use oxigraph::model::*;
use oxigraph::sparql::QueryResults;

use crate::compile::{CompiledShapes, Shape, Target};
use crate::constraints::Constraint;
use crate::functions::Functions;
use crate::graph::*;
use crate::{Error, Result};

#[derive(Clone, Debug)]
pub struct Options {
    pub iterate_rules: bool,
    pub max_rule_iterations: usize,
    pub max_validation_depth: usize,
    pub allow_infos: bool,
    pub allow_warnings: bool,
    pub abort_on_first: bool,
    pub focus_nodes: Vec<Term>,
    pub use_shapes: Vec<Term>,
    pub namespaces: Vec<(String, String)>,
}

impl Default for Options {
    fn default() -> Self {
        Self {
            iterate_rules: false,
            max_rule_iterations: 100,
            max_validation_depth: 15,
            allow_infos: false,
            allow_warnings: false,
            abort_on_first: false,
            focus_nodes: Vec::new(),
            use_shapes: Vec::new(),
            namespaces: Vec::new(),
        }
    }
}

pub struct ValidationReport {
    pub conforms: bool,
    pub graph: Dataset,
    pub text: String,
    pub recursion_warnings: Vec<String>,
}

pub struct RuleExpansion {
    pub graph: Dataset,
    pub recursion_warnings: Vec<String>,
}

#[derive(Clone, Copy)]
struct EvaluationStep {
    shape: usize,
    component: &'static str,
}

struct Evaluation {
    functions: Functions,
    path: Vec<EvaluationStep>,
    max_depth: usize,
    warnings: Vec<String>,
    batch: Option<EvaluationBatch>,
}

#[derive(Clone, Copy)]
struct EvaluationBatch {
    shape: usize,
    depth: usize,
    has_values: bool,
}

impl Evaluation {
    fn new(max_depth: usize) -> Self {
        Self {
            functions: Functions::default(),
            path: Vec::new(),
            max_depth,
            warnings: Vec::new(),
            batch: None,
        }
    }

    fn describe_path(&self, shapes: &[Shape], current: Option<EvaluationStep>) -> String {
        self.path
            .iter()
            .copied()
            .chain(current)
            .map(|step| format!("{} -> {}", shapes[step.shape].node, step.component))
            .collect::<Vec<_>>()
            .join(" -> ")
    }

    /// Match pySHACL's recursion_triggers: shape/constraint edges, not RDF nodes.
    fn skip_recursive(
        &mut self,
        shape: usize,
        component: &'static str,
        target: usize,
        shapes: &[Shape],
    ) -> bool {
        let alternating = self.path.last().is_some_and(|previous| {
            matches!(
                (previous.component, component),
                ("NodeConstraintComponent", "PropertyConstraintComponent")
                    | ("PropertyConstraintComponent", "NodeConstraintComponent")
            )
        });
        let depth = self.path.len() + 1;
        if depth < if alternating { 6 } else { 3 } {
            return false;
        }
        let recursive = self.path.iter().enumerate().any(|(i, step)| {
            step.shape == shape
                && step.component == component
                && self.path.get(i + 1).map_or(shape, |next| next.shape) == target
        });
        if recursive {
            let path = self.describe_path(shapes, Some(EvaluationStep { shape, component }));
            self.warnings.push(format!(
                "Warning, A Recursive Shape was detected executing a recursive validation sequence {} levels deep. Backing out.\n{path}\nFor reference, see https://www.w3.org/TR/shacl/#shapes-recursion",
                depth * 2
            ));
        }
        recursive
    }
}

struct Violation {
    shape: usize,
    focus: Term,
    component: NamedNode,
    message: String,
    value: Option<Term>,
    path: Option<Term>,
    details: Vec<Violation>,
    source_constraint: Option<Term>,
    messages: Option<Vec<Term>>,
}

impl CompiledShapes {
    /// Validate a consistent Store snapshot without RDF text conversion.
    /// Rule additions commit in one Store transaction only after success.
    pub fn validate_store(
        &self,
        store: &oxigraph::store::Store,
        options: Options,
        inplace: bool,
    ) -> Result<ValidationReport> {
        let before = store_snapshot(store)?;
        let mut working = before.clone();
        let report = self.validate(&mut working, options)?;
        if inplace {
            commit_store(store, &before, &working)?;
        }
        Ok(report)
    }

    /// Expand rules over a Store snapshot; optionally commit the additions.
    pub fn expand_store(
        &self,
        store: &oxigraph::store::Store,
        options: Options,
        inplace: bool,
    ) -> Result<RuleExpansion> {
        let before = store_snapshot(store)?;
        let mut working = before.clone();
        let recursion_warnings = self.expand_rules(&mut working, options)?;
        if inplace {
            commit_store(store, &before, &working)?;
        }
        Ok(RuleExpansion {
            graph: working,
            recursion_warnings,
        })
    }

    /// Inspect targets using the same evaluator as validation and rules.
    /// The caller supplies the default-union view, reusable across calls.
    pub fn shape_focus_nodes(
        &self,
        node: &str,
        data: &Dataset,
        advanced: bool,
    ) -> Result<Vec<Term>> {
        let shape = self
            .shapes
            .iter()
            .find(|shape| shape.node.to_string() == node)
            .ok_or_else(|| Error::Invalid(format!("Unknown shape: {node}")))?;
        self.focus_nodes_with_advanced(shape, data, advanced)
    }

    fn focus_nodes(&self, shape: &Shape, data: &Dataset) -> Result<Vec<Term>> {
        self.focus_nodes_with_advanced(shape, data, true)
    }

    /// Reverse declared targets for active node shapes. Data is a reusable
    /// default-union view. Skipped shapes are never evaluated.
    pub fn targeting_index(
        &self,
        data: &Dataset,
        skip: &HashSet<Term>,
    ) -> Result<HashMap<Term, Vec<Term>>> {
        let mut index: HashMap<Term, Vec<Term>> = HashMap::new();
        for shape in &self.shapes {
            if shape.deactivated || shape.path.is_some() || skip.contains(&shape.node) {
                continue;
            }
            for node in self.focus_nodes(shape, data)? {
                index.entry(node).or_default().push(shape.node.clone());
            }
        }
        for shapes in index.values_mut() {
            shapes.sort_by_key(ToString::to_string);
        }
        Ok(index)
    }

    fn focus_nodes_with_advanced(
        &self,
        shape: &Shape,
        data: &Dataset,
        advanced: bool,
    ) -> Result<Vec<Term>> {
        let mut nodes = HashSet::new();
        for target in &shape.targets {
            match target {
                Target::Node(node) => {
                    nodes.insert(node.clone());
                }
                Target::Class(class) => {
                    let mut pending = VecDeque::from([class.clone()]);
                    let mut visited = HashSet::new();
                    while let Some(class) = pending.pop_front() {
                        if !visited.insert(class.clone()) {
                            continue;
                        }
                        nodes.extend(subjects(data, &iri(RDF, "type"), Some(&class))?);
                        pending.extend(subjects(data, &iri(RDFS, "subClassOf"), Some(&class))?);
                    }
                }
                Target::Subjects(predicate) => {
                    nodes.extend(subjects(data, predicate, None)?);
                }
                Target::Objects(predicate) => {
                    for quad in data.quads_for_pattern(
                        None,
                        Some(predicate.as_ref()),
                        None,
                        Some(GraphNameRef::DefaultGraph),
                    ) {
                        nodes.insert(quad.object.into_owned());
                    }
                }
                Target::Sparql { query, bindings } => {
                    if !advanced {
                        continue;
                    }
                    let functions = self.functions.for_dataset(data);
                    let mut evaluation = query.prepare(&functions, data).on_queryable_dataset(data);
                    for (variable, value) in bindings {
                        evaluation =
                            evaluation.substitute_variable(variable.clone(), value.clone());
                    }
                    let QueryResults::Solutions(solutions) = evaluation.execute()? else {
                        return Err(Error::Invalid(
                            "SPARQL target did not return SELECT results".into(),
                        ));
                    };
                    if !solutions.variables().iter().any(|v| v.as_str() == "this") {
                        return Err(Error::Invalid("SPARQL target must project ?this".into()));
                    }
                    for solution in solutions {
                        let solution = solution?;
                        let node = solution.get("this").ok_or_else(|| {
                            Error::Invalid("SPARQL target returned an unbound ?this".into())
                        })?;
                        nodes.insert(node.clone());
                    }
                }
            }
        }
        let mut nodes: Vec<_> = nodes.into_iter().collect();
        nodes.sort_by_key(ToString::to_string);
        Ok(nodes)
    }

    #[allow(clippy::too_many_arguments)]
    fn evaluate_child(
        &self,
        parent: usize,
        component: &'static str,
        index: usize,
        focus: &Term,
        data: &Dataset,
        results: &mut Vec<Violation>,
        evaluation: &mut Evaluation,
    ) -> Result<()> {
        evaluation.path.push(EvaluationStep {
            shape: parent,
            component,
        });
        let result = self.evaluate_batch(
            index,
            std::slice::from_ref(focus),
            data,
            results,
            evaluation,
        );
        evaluation.path.pop();
        result
    }

    fn evaluate_batch(
        &self,
        index: usize,
        focus: &[Term],
        data: &Dataset,
        results: &mut Vec<Violation>,
        evaluation: &mut Evaluation,
    ) -> Result<()> {
        let shape = &self.shapes[index];
        let batch = if focus.len() > 1
            && !shape.deactivated
            && shape
                .constraints
                .iter()
                .any(|constraint| matches!(constraint, Constraint::Qualified { .. }))
        {
            // pySHACL's qualified-count empty-input shortcut applies to the
            // whole focus batch. Nested property validations receive one
            // focus each, so their scopes must not inherit this batch.
            let mut has_values = shape.path.is_none();
            if let Some(path) = &shape.path {
                for node in focus {
                    if !path.values(data, node)?.is_empty() {
                        has_values = true;
                        break;
                    }
                }
            }
            Some(EvaluationBatch {
                shape: index,
                depth: evaluation.path.len(),
                has_values,
            })
        } else {
            None
        };
        let previous = std::mem::replace(&mut evaluation.batch, batch);
        let result = focus
            .iter()
            .try_for_each(|node| self.evaluate_inner(index, node, data, results, evaluation));
        evaluation.batch = previous;
        result
    }

    fn evaluate_inner(
        &self,
        index: usize,
        focus: &Term,
        data: &Dataset,
        results: &mut Vec<Violation>,
        evaluation: &mut Evaluation,
    ) -> Result<()> {
        let functions = evaluation.functions.clone();
        let shape = &self.shapes[index];
        if shape.deactivated {
            return Ok(());
        }
        if evaluation.path.len() >= evaluation.max_depth {
            return Err(Error::Runtime(format!(
                "Validation path too deep!\n{}",
                evaluation.describe_path(&self.shapes, None)
            )));
        }
        let values = if let Some(path) = &shape.path {
            path.values(data, focus)?
        } else {
            vec![focus.clone()]
        };
        let violation = |component, value: Option<&Term>| Violation {
            shape: index,
            focus: focus.clone(),
            component: iri(SH, component),
            message: String::new(),
            value: value.cloned(),
            path: shape.path_node.clone(),
            details: Vec::new(),
            source_constraint: None,
            messages: None,
        };
        for constraint in &shape.constraints {
            match constraint {
                Constraint::NodeExpression {
                    expression,
                    node,
                    messages,
                } => {
                    for value in &values {
                        let nodes = expression.evaluate(value, data, &functions, &mut |i, n| {
                            let mut nested = Vec::new();
                            self.evaluate_child(
                                index,
                                "ExpressionConstraintComponent",
                                i,
                                n,
                                data,
                                &mut nested,
                                evaluation,
                            )?;
                            Ok(nested.is_empty())
                        })?;
                        if nodes != HashSet::from([Literal::from(true).into()]) {
                            let mut result =
                                violation("ExpressionConstraintComponent", Some(value));
                            result.source_constraint = Some(node.clone());
                            if !messages.is_empty() {
                                result.messages = Some(messages.clone());
                            }
                            results.push(result);
                        }
                    }
                }
                Constraint::Sparql(query) => {
                    let inputs = if query.per_value {
                        values.iter().map(Some).collect()
                    } else {
                        vec![None]
                    };
                    for input in inputs {
                        for row in query.evaluate(
                            data,
                            &self.graph,
                            &shape.node,
                            focus,
                            &shape.messages,
                            input,
                            &functions,
                        )? {
                            let mut result =
                                violation("SPARQLConstraintComponent", row.value.as_ref());
                            result.focus = row.focus;
                            if result.value.is_none() && shape.path.is_none() {
                                result.value = Some(focus.clone());
                            }
                            if query.per_value && shape.path.is_some() {
                                // Match pySHACL's optional sh:value omission for
                                // ASK validators attached to property shapes.
                                result.value = None;
                            }
                            if row.path.is_some() {
                                result.path = row.path;
                            }
                            if let Some(component) = &query.component {
                                result.component = component.clone();
                            } else {
                                result.source_constraint = Some(query.node.clone());
                            }
                            if !row.messages.is_empty() {
                                result.messages = Some(row.messages);
                            }
                            results.push(result);
                        }
                    }
                }
                Constraint::Count { minimum, count } => {
                    if !count.allows(values.len(), *minimum) {
                        results.push(violation(
                            if *minimum {
                                "MinCountConstraintComponent"
                            } else {
                                "MaxCountConstraintComponent"
                            },
                            None,
                        ));
                    }
                }
                Constraint::HasValue(required) => {
                    if !values.contains(required) {
                        results.push(violation("HasValueConstraintComponent", None));
                    }
                }
                Constraint::Class(class) => {
                    for value in &values {
                        if !is_instance(data, value, class)? {
                            results.push(violation("ClassConstraintComponent", Some(value)));
                        }
                    }
                }
                Constraint::Datatype(datatype) => {
                    for value in &values {
                        if !crate::value::datatype(value, datatype) {
                            results.push(violation("DatatypeConstraintComponent", Some(value)));
                        }
                    }
                }
                Constraint::NodeKind(kind) => {
                    for value in &values {
                        let valid = match value {
                            Term::NamedNode(_) => {
                                ["IRI", "BlankNodeOrIRI", "IRIOrLiteral"].contains(&kind.as_str())
                            }
                            Term::BlankNode(_) => {
                                ["BlankNode", "BlankNodeOrIRI", "BlankNodeOrLiteral"]
                                    .contains(&kind.as_str())
                            }
                            Term::Literal(_) => ["Literal", "BlankNodeOrLiteral", "IRIOrLiteral"]
                                .contains(&kind.as_str()),
                        };
                        if !valid {
                            results.push(violation("NodeKindConstraintComponent", Some(value)));
                        }
                    }
                }
                Constraint::Pattern(regex) => {
                    for value in &values {
                        let valid = crate::value::lexical(value)
                            .map(|text| regex.is_match(text))
                            .transpose()?
                            .unwrap_or(false);
                        if !valid {
                            results.push(violation("PatternConstraintComponent", Some(value)));
                        }
                    }
                }
                Constraint::Expression { component, query } => {
                    for value in &values {
                        if !crate::value::expression(query, data, value, None)? {
                            results.push(violation(component, Some(value)));
                        }
                    }
                }
                Constraint::Length { minimum, count } => {
                    for value in &values {
                        let valid = (*minimum && count.is_zero())
                            || crate::value::lexical(value)
                                .is_some_and(|s| count.allows(s.chars().count(), *minimum));
                        if !valid {
                            results.push(violation(
                                if *minimum {
                                    "MinLengthConstraintComponent"
                                } else {
                                    "MaxLengthConstraintComponent"
                                },
                                Some(value),
                            ));
                        }
                    }
                }
                Constraint::LanguageIn(ranges) => {
                    for value in &values {
                        let valid = if let Term::Literal(l) = value {
                            l.language().is_some_and(|lang| {
                                ranges.iter().any(|r| {
                                    r == "*"
                                        || lang == r
                                        || lang
                                            .strip_prefix(r)
                                            .is_some_and(|suffix| suffix.starts_with('-'))
                                })
                            })
                        } else {
                            false
                        };
                        if !valid {
                            results.push(violation("LanguageInConstraintComponent", Some(value)));
                        }
                    }
                }
                Constraint::UniqueLang => {
                    let mut seen = HashSet::new();
                    let mut repeated = HashSet::new();
                    for value in &values {
                        if let Term::Literal(l) = value
                            && let Some(lang) = l.language()
                            && !seen.insert(lang)
                        {
                            repeated.insert(lang);
                        }
                    }
                    for _ in repeated {
                        results.push(violation("UniqueLangConstraintComponent", None));
                    }
                }
                Constraint::In(allowed) => {
                    for value in &values {
                        if !allowed.contains(value) {
                            results.push(violation("InConstraintComponent", Some(value)));
                        }
                    }
                }
                Constraint::Pair {
                    kind,
                    predicate,
                    query,
                } => {
                    let others = objects(data, focus, predicate)?;
                    if let Some(query) = query {
                        for value in &values {
                            for other in &others {
                                if !crate::value::expression(query, data, value, Some(other))? {
                                    results.push(violation(kind, Some(value)));
                                }
                            }
                        }
                    } else if *kind == "EqualsConstraintComponent" {
                        for value in values
                            .iter()
                            .filter(|v| !others.contains(v))
                            .chain(others.iter().filter(|v| !values.contains(v)))
                        {
                            results.push(violation(kind, Some(value)));
                        }
                    } else {
                        for value in values.iter().filter(|v| others.contains(v)) {
                            results.push(violation(kind, Some(value)));
                        }
                    }
                }
                Constraint::Node(target) => {
                    if !values.is_empty()
                        && evaluation.skip_recursive(
                            index,
                            "NodeConstraintComponent",
                            *target,
                            &self.shapes,
                        )
                    {
                        continue;
                    }
                    for value in &values {
                        let mut details = Vec::new();
                        self.evaluate_child(
                            index,
                            "NodeConstraintComponent",
                            *target,
                            value,
                            data,
                            &mut details,
                            evaluation,
                        )?;
                        if !details.is_empty() {
                            let mut parent = violation("NodeConstraintComponent", Some(value));
                            parent.details = details;
                            results.push(parent);
                        }
                    }
                }
                Constraint::Logical { kind, shapes } => {
                    // Only sh:not has the reference warn-and-skip policy.
                    // and/or/xone recursion is bounded by max_validation_depth.
                    if *kind == "NotConstraintComponent"
                        && shapes.iter().any(|&target| {
                            evaluation.skip_recursive(index, kind, target, &self.shapes)
                        })
                    {
                        continue;
                    }
                    for value in &values {
                        let mut count = 0;
                        for &target in shapes {
                            let mut nested = Vec::new();
                            self.evaluate_child(
                                index,
                                kind,
                                target,
                                value,
                                data,
                                &mut nested,
                                evaluation,
                            )?;
                            count += usize::from(nested.is_empty());
                        }
                        let valid = match *kind {
                            "NotConstraintComponent" => count == 0,
                            "AndConstraintComponent" => count == shapes.len(),
                            "OrConstraintComponent" => count > 0,
                            "XoneConstraintComponent" => count == 1,
                            _ => unreachable!(),
                        };
                        if !valid {
                            results.push(violation(kind, Some(value)));
                        }
                    }
                }
                Constraint::Qualified {
                    shape: target,
                    minimum,
                    maximum,
                    disjoint,
                    siblings,
                } => {
                    let has_values = evaluation
                        .batch
                        .filter(|batch| {
                            batch.shape == index && batch.depth == evaluation.path.len()
                        })
                        .map_or(!values.is_empty(), |batch| batch.has_values);
                    if !has_values
                        && !disjoint
                        && minimum.as_ref().is_none_or(|min| min.allows(0, true))
                    {
                        continue;
                    }
                    if evaluation.skip_recursive(
                        index,
                        "QualifiedValueShapeConstraintComponent",
                        *target,
                        &self.shapes,
                    ) {
                        continue;
                    }
                    let mut count = 0usize;
                    for value in &values {
                        let mut nested = Vec::new();
                        self.evaluate_child(
                            index,
                            "QualifiedValueShapeConstraintComponent",
                            *target,
                            value,
                            data,
                            &mut nested,
                            evaluation,
                        )?;
                        if !nested.is_empty() {
                            continue;
                        }
                        let mut disjoint = true;
                        for &sibling in siblings {
                            let mut sibling_results = Vec::new();
                            self.evaluate_child(
                                index,
                                "QualifiedValueShapeConstraintComponent",
                                sibling,
                                value,
                                data,
                                &mut sibling_results,
                                evaluation,
                            )?;
                            if sibling_results.is_empty() {
                                disjoint = false;
                                break;
                            }
                        }
                        count += usize::from(disjoint);
                    }
                    if minimum.as_ref().is_some_and(|min| !min.allows(count, true)) {
                        results.push(violation("QualifiedMinCountConstraintComponent", None));
                    }
                    if maximum
                        .as_ref()
                        .is_some_and(|max| !max.allows(count, false))
                    {
                        results.push(violation("QualifiedMaxCountConstraintComponent", None));
                    }
                }
                Constraint::Closed(allowed) => {
                    for value in &values {
                        let Ok(node) = subject(value) else {
                            continue;
                        };
                        for quad in data.quads_for_pattern(
                            Some(node.as_ref()),
                            None,
                            None,
                            Some(GraphNameRef::DefaultGraph),
                        ) {
                            let quad = quad.into_owned();
                            if quad.predicate == iri(RDF, "type")
                                && quad.object == Term::from(iri(RDFS, "Resource"))
                            {
                                continue;
                            }
                            if !allowed.contains(&quad.predicate) {
                                let mut result =
                                    violation("ClosedConstraintComponent", Some(&quad.object));
                                result.path = Some(quad.predicate.into());
                                results.push(result);
                            }
                        }
                    }
                }
            }
        }
        for &property in &shape.properties {
            if !values.is_empty()
                && evaluation.skip_recursive(
                    index,
                    "PropertyConstraintComponent",
                    property,
                    &self.shapes,
                )
            {
                continue;
            }
            for value in &values {
                self.evaluate_child(
                    index,
                    "PropertyConstraintComponent",
                    property,
                    value,
                    data,
                    results,
                    evaluation,
                )?;
            }
        }
        Ok(())
    }

    /// Mutates only this explicitly supplied store. Python validates a fresh store
    /// and commits additions to the caller's Graph only after successful execution.
    fn has_active_rules(&self, options: &Options) -> bool {
        self.execution_order.iter().any(|&index| {
            let shape = &self.shapes[index];
            (options.use_shapes.is_empty() || options.use_shapes.contains(&shape.node))
                && shape.rules.iter().any(|rule| !rule.deactivated)
        })
    }

    pub fn expand_rules(&self, data: &mut Dataset, options: Options) -> Result<Vec<String>> {
        if self.has_active_rules(&options) && data.iter().any(|q| !q.graph_name.is_default_graph())
        {
            return Ok(self.expand_rules_delta(data, options)?.recursion_warnings);
        }
        self.expand_rules_inner(data, options, None)
    }

    /// Expand rules while retaining only successfully inserted statements.
    pub fn expand_rules_delta(
        &self,
        data: &mut Dataset,
        options: Options,
    ) -> Result<RuleExpansion> {
        let mut additions = Dataset::new();
        let recursion_warnings = if self.has_active_rules(&options)
            && data.iter().any(|q| !q.graph_name.is_default_graph())
        {
            let mut working = with_union(data);
            let warnings = self.expand_rules_inner(&mut working, options, Some(&mut additions))?;
            data.extend(additions.iter());
            warnings
        } else {
            self.expand_rules_inner(data, options, Some(&mut additions))?
        };
        Ok(RuleExpansion {
            graph: additions,
            recursion_warnings,
        })
    }

    fn expand_rules_inner(
        &self,
        data: &mut Dataset,
        options: Options,
        mut delta: Option<&mut Dataset>,
    ) -> Result<Vec<String>> {
        if options.max_rule_iterations == 0 {
            return Err(Error::Invalid(
                "max_rule_iterations must be positive".into(),
            ));
        }
        let mut evaluation = Evaluation::new(options.max_validation_depth);
        for &index in &self.execution_order {
            let shape = &self.shapes[index];
            if !options.use_shapes.is_empty() && !options.use_shapes.contains(&shape.node) {
                continue;
            }
            if shape.rules.is_empty() {
                continue;
            }
            let mut pass = 0;
            loop {
                if pass == options.max_rule_iterations {
                    return Err(Error::Runtime(format!(
                        "Rule iteration limit ({}) exceeded for {}",
                        options.max_rule_iterations, shape.node
                    )));
                }
                pass += 1;
                let mut changed = false;
                for rule in &shape.rules {
                    if rule.deactivated {
                        continue;
                    }
                    let focus = self.selected_focus_nodes(shape, data, &options)?;
                    let functions = self.functions.for_dataset(data);
                    evaluation.functions = functions.clone();
                    let mut additions = HashSet::new();
                    for node in focus {
                        let mut condition_results = Vec::new();
                        for &condition in &rule.conditions {
                            self.evaluate_batch(
                                condition,
                                std::slice::from_ref(&node),
                                data,
                                &mut condition_results,
                                &mut evaluation,
                            )?;
                        }
                        if !condition_results.is_empty() {
                            continue;
                        }
                        if let Some(expressions) = &rule.triple {
                            let mut filter = |i, n: &Term| {
                                let mut results = Vec::new();
                                self.evaluate_batch(
                                    i,
                                    std::slice::from_ref(n),
                                    data,
                                    &mut results,
                                    &mut evaluation,
                                )?;
                                Ok(results.is_empty())
                            };
                            let subjects =
                                expressions[0].evaluate(&node, data, &functions, &mut filter)?;
                            let predicates =
                                expressions[1].evaluate(&node, data, &functions, &mut filter)?;
                            let objects =
                                expressions[2].evaluate(&node, data, &functions, &mut filter)?;
                            for s in subjects {
                                for p in &predicates {
                                    for o in &objects {
                                        additions.insert(Quad::new(
                                            subject(&s)?,
                                            crate::constraints::named(
                                                p.clone(),
                                                "TripleRule predicate",
                                            )?,
                                            o.clone(),
                                            GraphName::DefaultGraph,
                                        ));
                                    }
                                }
                            }
                        }
                        for query in &rule.queries {
                            let result = query
                                .prepare(&functions, data)
                                .on_queryable_dataset(&*data)
                                .substitute_variable(Variable::new_unchecked("this"), node.clone())
                                .execute()?;
                            let QueryResults::Graph(triples) = result else {
                                return Err(Error::Invalid(
                                    "SPARQL rule did not return CONSTRUCT triples".into(),
                                ));
                            };
                            for triple in triples {
                                let triple = triple?;
                                additions.insert(Quad::new(
                                    triple.subject,
                                    triple.predicate,
                                    triple.object,
                                    GraphName::DefaultGraph,
                                ));
                            }
                        }
                    }
                    // All focus nodes of a rule see the same snapshot; subsequent
                    // rules see the complete batch of additions.
                    for quad in additions {
                        if data.insert(&quad) {
                            if let Some(delta) = delta.as_deref_mut() {
                                delta.insert(&quad);
                            }
                            changed = true;
                        }
                    }
                }
                if !options.iterate_rules || !changed {
                    break;
                }
            }
        }
        Ok(evaluation.warnings)
    }

    fn selected_focus_nodes(
        &self,
        shape: &Shape,
        data: &Dataset,
        options: &Options,
    ) -> Result<Vec<Term>> {
        if !options.use_shapes.is_empty() && !options.focus_nodes.is_empty() {
            return Ok(options.focus_nodes.clone());
        }
        let mut nodes = self.focus_nodes(shape, data)?;
        if !options.focus_nodes.is_empty() {
            nodes.retain(|node| options.focus_nodes.contains(node));
        }
        Ok(nodes)
    }

    /// Expand rules, then discover validation targets on the resulting graph.
    pub fn validate(&self, data: &mut Dataset, options: Options) -> Result<ValidationReport> {
        let mut evaluation = Evaluation::new(options.max_validation_depth);
        evaluation.warnings = self.expand_rules(data, options.clone())?;
        let display_data = &*data;
        let joined;
        let data = if data.iter().any(|q| !q.graph_name.is_default_graph()) {
            joined = with_union(data);
            &joined
        } else {
            &*data
        };
        evaluation.functions = self.functions.for_dataset(data);
        let mut violations = Vec::new();
        for &index in &self.execution_order {
            let shape = &self.shapes[index];
            if !options.use_shapes.is_empty() && !options.use_shapes.contains(&shape.node) {
                continue;
            }
            if shape.deactivated {
                continue;
            }
            let focus_nodes = self.selected_focus_nodes(shape, data, &options)?;
            self.evaluate_batch(index, &focus_nodes, data, &mut violations, &mut evaluation)?;
            if options.abort_on_first && !violations.is_empty() {
                break;
            }
        }
        let conforms = violations.iter().all(|v| {
            let severity = &self.shapes[v.shape].severity;
            (options.allow_warnings && severity == &iri(SH, "Warning"))
                || ((options.allow_infos || options.allow_warnings) && severity == &iri(SH, "Info"))
        });
        let mut report = Dataset::new();
        let root: Term = BlankNode::default().into();
        add(
            &mut report,
            &root,
            iri(RDF, "type"),
            iri(SH, "ValidationReport").into(),
        )?;
        add(
            &mut report,
            &root,
            iri(SH, "conforms"),
            Literal::from(conforms).into(),
        )?;
        let mut text = format!(
            "Validation Report\nConforms: {}\n",
            if conforms { "True" } else { "False" }
        );
        if !violations.is_empty() {
            text.push_str(&format!("Results ({}):\n", violations.len()));
        }
        let mut shape_namespaces = self.namespaces.clone();
        let mut data_namespaces = options.namespaces;
        for (p, ns) in [("sh", SH), ("rdf", RDF), ("rdfs", RDFS), ("xsd", XSD)] {
            shape_namespaces.push((p.into(), ns.into()));
            data_namespaces.push((p.into(), ns.into()));
        }
        let display = crate::display::Display {
            shape_namespaces,
            data_namespaces,
            data: display_data,
            shapes: &self.graph,
        };
        let mut clones = ReportClones::default();
        let mut descriptions = Vec::new();
        for violation in &violations {
            let mut description = String::new();
            self.write_result(
                &mut report,
                &root,
                "result",
                violation,
                data,
                &mut description,
                &mut clones,
                &display,
            )?;
            descriptions.push(description);
        }
        descriptions.sort();
        for description in descriptions {
            text.push_str(&description);
        }
        Ok(ValidationReport {
            conforms,
            graph: report,
            text,
            recursion_warnings: evaluation.warnings,
        })
    }
    #[allow(clippy::too_many_arguments)]
    fn write_result(
        &self,
        report: &mut Dataset,
        parent: &Term,
        edge: &str,
        violation: &Violation,
        data: &Dataset,
        text: &mut String,
        clones: &mut ReportClones,
        display: &crate::display::Display<'_>,
    ) -> Result<()> {
        let shape = &self.shapes[violation.shape];
        let result: Term = BlankNode::default().into();
        add(report, parent, iri(SH, edge), result.clone())?;
        for (predicate, object) in [
            (iri(RDF, "type"), iri(SH, "ValidationResult").into()),
            (
                iri(SH, "sourceConstraintComponent"),
                violation.component.clone().into(),
            ),
            (iri(SH, "sourceShape"), shape.node.clone()),
            (iri(SH, "resultSeverity"), shape.severity.clone().into()),
            (iri(SH, "focusNode"), violation.focus.clone()),
        ] {
            add(report, &result, predicate, object)?;
        }
        clones.copy(&self.graph, report, &shape.node)?;
        clones.copy(data, report, &violation.focus)?;
        if let Some(path) = &violation.path {
            add(report, &result, iri(SH, "resultPath"), path.clone())?;
            clones.copy(&self.graph, report, path)?;
        }
        if let Some(value) = &violation.value {
            add(report, &result, iri(SH, "value"), value.clone())?;
            clones.copy(data, report, value)?;
        }
        if let Some(constraint) = &violation.source_constraint {
            add(
                report,
                &result,
                iri(SH, "sourceConstraint"),
                constraint.clone(),
            )?;
            clones.copy(&self.graph, report, constraint)?;
        }
        let messages = if let Some(messages) = &violation.messages {
            messages.clone()
        } else if shape.messages.is_empty() {
            let message = if !violation.message.is_empty() {
                violation.message.clone()
            } else {
                let focus = display.term(&violation.focus, false);
                let component = violation
                    .component
                    .as_str()
                    .strip_prefix(SH)
                    .unwrap_or(violation.component.as_str());
                match component {
                    "MinCountConstraintComponent" | "MaxCountConstraintComponent" => {
                        let minimum = component == "MinCountConstraintComponent";
                        let count = shape
                            .constraints
                            .iter()
                            .find_map(|constraint| match constraint {
                                Constraint::Count {
                                    minimum: is_minimum,
                                    count,
                                } if *is_minimum == minimum => Some(count),
                                _ => None,
                            })
                            .expect("cardinality violation requires a compiled count constraint");
                        let direction = if minimum { "Less" } else { "More" };
                        let location = if let Some(path) = &violation.path {
                            format!("{focus}->{}", display.term(path, true))
                        } else {
                            focus
                        };
                        format!("{direction} than {count} values on {location}")
                    }
                    "MinLengthConstraintComponent" | "MaxLengthConstraintComponent" => {
                        let minimum = component == "MinLengthConstraintComponent";
                        let count = shape
                            .constraints
                            .iter()
                            .find_map(|constraint| match constraint {
                                Constraint::Length {
                                    minimum: is_minimum,
                                    count,
                                } if *is_minimum == minimum => Some(count),
                                _ => None,
                            })
                            .expect("length violation requires a compiled length constraint");
                        let number = count.number.to_string();
                        let lexical = count.literal.value();
                        let value = if lexical == number {
                            format!("\"{lexical}\"")
                        } else {
                            format!("\"{lexical}\" = {number}")
                        };
                        let operator = if minimum { ">=" } else { "<=" };
                        format!(
                            "String length not {operator} Literal({value}, datatype={})",
                            display.iri(&count.literal.datatype().into_owned())
                        )
                    }
                    "QualifiedMinCountConstraintComponent"
                    | "QualifiedMaxCountConstraintComponent" => {
                        let (target, minimum, maximum) = shape
                            .constraints
                            .iter()
                            .find_map(|constraint| match constraint {
                                Constraint::Qualified {
                                    shape,
                                    minimum,
                                    maximum,
                                    ..
                                } => Some((*shape, minimum, maximum)),
                                _ => None,
                            })
                            .expect("qualified violation requires a compiled qualified constraint");
                        let mut counts = String::new();
                        if let Some(minimum) = minimum {
                            counts.push_str(&format!(" MinCount {minimum}"));
                        }
                        if let Some(maximum) = maximum {
                            counts.push_str(&format!(" MaxCount {maximum}"));
                        }
                        format!(
                            "Focus node does not conform to shape{counts}: {}",
                            display.term(&self.shapes[target].node, true)
                        )
                    }
                    "PatternConstraintComponent" => {
                        let patterns = values(&self.graph, &shape.node, "pattern")?
                            .iter()
                            .filter_map(crate::value::lexical)
                            .map(str::to_owned)
                            .collect::<Vec<_>>();
                        if patterns.len() == 1 {
                            format!("Value does not match pattern '{}'", patterns[0])
                        } else {
                            format!(
                                "Value does not match every pattern in ('{}')",
                                patterns.join("', '")
                            )
                        }
                    }
                    "ClassConstraintComponent" => {
                        let mut classes = values(&self.graph, &shape.node, "class")?
                            .iter()
                            .map(|n| display.term(n, true))
                            .collect::<Vec<_>>();
                        classes.sort();
                        if classes.len() == 1 {
                            format!("Value does not have class {}", classes[0])
                        } else {
                            format!("Value class is not in classes ({})", classes.join(", "))
                        }
                    }
                    "NodeConstraintComponent" => {
                        let mut nodes = values(&self.graph, &shape.node, "node")?
                            .iter()
                            .map(|n| format!("'{}'", display.term(n, true)))
                            .collect::<Vec<_>>();
                        nodes.sort();
                        if nodes.len() == 1 {
                            format!(
                                "Value does not conform to Shape {}. See details for more information.",
                                nodes[0]
                            )
                        } else {
                            format!(
                                "Value must conform to every Shape in ({})",
                                nodes.join(", ")
                            )
                        }
                    }
                    "NotConstraintComponent" => {
                        let mut nodes = values(&self.graph, &shape.node, "not")?
                            .iter()
                            .map(|n| display.term(n, true))
                            .collect::<Vec<_>>();
                        nodes.sort();
                        format!(
                            "Node {focus} must not conform to shape {}",
                            nodes.join(", ")
                        )
                    }
                    _ => format!("{component} violated at {focus}"),
                }
            };
            vec![Literal::new_simple_literal(message).into()]
        } else {
            shape.messages.clone()
        };
        let component = violation
            .component
            .as_str()
            .strip_prefix(SH)
            .unwrap_or(violation.component.as_str());
        let title = if [
            "QualifiedMinCountConstraintComponent",
            "QualifiedMaxCountConstraintComponent",
        ]
        .contains(&component)
        {
            "QualifiedValueShapeConstraintComponent"
        } else {
            component
        };
        let category = if shape.severity == iri(SH, "Violation") {
            "Constraint Violation"
        } else {
            "Validation Result"
        };
        text.push_str(&format!(
            "{category} in {title} ({}):\n\tSeverity: {}\n\tSource Shape: {}\n\tFocus Node: {}\n",
            violation.component.as_str(),
            display.iri(&shape.severity),
            display.term(&shape.node, true),
            display.term(&violation.focus, false)
        ));
        if let Some(value) = &violation.value {
            text.push_str(&format!("\tValue Node: {}\n", display.term(value, false)));
        }
        if let Some(path) = &violation.path {
            text.push_str(&format!("\tResult Path: {}\n", display.term(path, true)));
        }
        if let Some(source) = &violation.source_constraint {
            text.push_str(&format!(
                "\tSource Constraint: {}\n",
                display.term(source, true)
            ));
        }
        let mut messages = messages;
        messages.sort_by_key(ToString::to_string);
        for message in messages {
            let printed = match &message {
                Term::Literal(l) => l.value().to_owned(),
                _ => message.to_string(),
            };
            text.push_str(&format!("\tMessage: {printed}\n"));
            add(report, &result, iri(SH, "resultMessage"), message)?;
        }
        let mut descriptions = Vec::new();
        for detail in &violation.details {
            let mut description = String::new();
            self.write_result(
                report,
                &result,
                "detail",
                detail,
                data,
                &mut description,
                clones,
                display,
            )?;
            descriptions.push(description);
        }
        descriptions.sort();
        if !descriptions.is_empty() {
            text.push_str("\tDetails:\n");
        }
        for description in descriptions {
            for line in description.lines() {
                text.push_str(&format!("\t\t{line}\n"));
            }
        }
        Ok(())
    }
}

fn is_instance(data: &Dataset, value: &Term, class: &Term) -> Result<bool> {
    let mut pending = objects(data, value, &iri(RDF, "type"))?;
    let mut seen = HashSet::new();
    while let Some(current) = pending.pop() {
        if &current == class {
            return Ok(true);
        }
        if seen.insert(current.clone()) {
            pending.extend(objects(data, &current, &iri(RDFS, "subClassOf"))?);
        }
    }
    Ok(false)
}

fn store_snapshot(store: &oxigraph::store::Store) -> Result<Dataset> {
    store
        .iter()
        .map(|q| q.map(store_quad))
        .collect::<std::result::Result<Dataset, _>>()
        .map_err(|e| Error::Runtime(format!("Store snapshot failed: {e}")))
}

fn commit_store(store: &oxigraph::store::Store, before: &Dataset, after: &Dataset) -> Result<()> {
    store
        .extend(
            after
                .iter()
                .filter(|q| !before.contains(*q))
                .map(|q| q.into_owned()),
        )
        .map_err(|e| Error::Runtime(format!("Store commit failed: {e}")))
}

#[cfg(test)]
mod union_tests {
    use super::*;
    use oxigraph::io::RdfFormat;

    #[test]
    fn validation_without_active_rules_builds_only_its_validation_union() {
        let shapes = parse("@prefix sh:<http://www.w3.org/ns/shacl#> . <urn:S> sh:targetNode <urn:s>; sh:path <urn:p>; sh:minCount 1.", RdfFormat::Turtle, None).unwrap();
        let program = CompiledShapes::compile(shapes, true).unwrap();
        let mut data =
            parse_dataset("<urn:g> { <urn:s> <urn:p> 1 }", RdfFormat::TriG, None).unwrap();
        UNION_BUILDS.with(|count| count.set(0));
        assert!(
            program
                .validate(&mut data, Options::default())
                .unwrap()
                .conforms
        );
        assert_eq!(UNION_BUILDS.with(std::cell::Cell::get), 1);
        assert_eq!(data.len(), 1);
        assert!(!data.iter().any(|q| q.graph_name.is_default_graph()));
        assert!(
            program
                .expand_rules(
                    &mut data,
                    Options {
                        max_rule_iterations: 0,
                        ..Options::default()
                    }
                )
                .is_err()
        );
    }
}

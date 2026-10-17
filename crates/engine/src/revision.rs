//! Source identity for two independently built copies of the canonical engine.
use sha2::{Digest, Sha256};

pub const SOURCES: &[(&str, &[u8])] = &[
    ("compile.rs", include_bytes!("compile.rs")),
    ("components.rs", include_bytes!("components.rs")),
    ("constraints.rs", include_bytes!("constraints.rs")),
    ("display.rs", include_bytes!("display.rs")),
    ("execute.rs", include_bytes!("execute.rs")),
    ("expression.rs", include_bytes!("expression.rs")),
    ("functions.rs", include_bytes!("functions.rs")),
    ("graph.rs", include_bytes!("graph.rs")),
    ("inference.rs", include_bytes!("inference.rs")),
    ("inference/axioms.rs", include_bytes!("inference/axioms.rs")),
    ("lib.rs", include_bytes!("lib.rs")),
    ("ontology.rs", include_bytes!("ontology.rs")),
    ("path.rs", include_bytes!("path.rs")),
    ("pattern.rs", include_bytes!("pattern.rs")),
    ("revision.rs", include_bytes!("revision.rs")),
    ("sparql.rs", include_bytes!("sparql.rs")),
    ("sparql_regex.rs", include_bytes!("sparql_regex.rs")),
    ("structural.rs", include_bytes!("structural.rs")),
    ("value.rs", include_bytes!("value.rs")),
];

pub fn fingerprint() -> String {
    let mut digest = Sha256::new();
    digest.update(include_bytes!("../Cargo.toml"));
    for (name, source) in SOURCES {
        digest.update(name.as_bytes());
        digest.update([0]);
        digest.update(source);
        digest.update([0]);
    }
    digest
        .finalize()
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

#[cfg(test)]
mod tests {
    #[test]
    fn fingerprint_covers_every_engine_implementation_file() {
        fn visit(root: &std::path::Path, directory: &std::path::Path, names: &mut Vec<String>) {
            for entry in std::fs::read_dir(directory).unwrap() {
                let path = entry.unwrap().path();
                if path.is_dir() {
                    visit(root, &path, names);
                } else if path.extension().is_some_and(|value| value == "rs")
                    && !path
                        .file_name()
                        .unwrap()
                        .to_str()
                        .unwrap()
                        .ends_with("_tests.rs")
                {
                    names.push(
                        path.strip_prefix(root)
                            .unwrap()
                            .to_str()
                            .unwrap()
                            .replace('\\', "/"),
                    );
                }
            }
        }
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
        let mut names = Vec::new();
        visit(&root, &root, &mut names);
        names.sort();
        assert_eq!(
            names,
            super::SOURCES
                .iter()
                .map(|(name, _)| name.to_string())
                .collect::<Vec<_>>()
        );
        assert_eq!(super::fingerprint().len(), 64);
    }
}

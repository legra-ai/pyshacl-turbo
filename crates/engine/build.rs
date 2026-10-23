use std::env;

use rhusky::Rhusky;

fn main() {
    for variable in ["RHUSKY_REPOSITORY_ROOT", "CI", "GITHUB_ACTIONS"] {
        println!("cargo::rerun-if-env-changed={variable}");
    }
    let Some(repository_root) = env::var_os("RHUSKY_REPOSITORY_ROOT") else {
        return;
    };
    Rhusky::new()
        .hooks_dir(".githooks")
        .skip_in_env("CI")
        .skip_in_env("GITHUB_ACTIONS")
        .with_default_hooks()
        .install_from_build_script(repository_root)
        .expect("failed to install repository Git hooks");
}

"""Build receipts bind actual tools, effective launch variables and Cargo configurations."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def helper():
    spec = importlib.util.spec_from_file_location(
        "benchmark_launch", ROOT / "scripts/benchmark_launch.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_launch_receipt_preserves_wrappers_without_collecting_registry_credentials(
    monkeypatch, tmp_path
):
    module = helper()
    monkeypatch.setattr(module, "tools", lambda env: {"uv": {"version": "uv 0.13.5"}})
    owner = tmp_path / "source"
    (owner / ".cargo").mkdir(parents=True)
    (owner / ".cargo/config.toml").write_text('[build]\nrustc-wrapper="sccache"\n')
    env = {
        "HOME": str(tmp_path / "home"),
        "CARGO_HOME": str(tmp_path / "cargo-home"),
        "RUSTUP_TOOLCHAIN": "1.99.1",
        "RUSTC_WRAPPER": "/configured/sccache",
        "CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER": "/configured/workspace-wrapper",
        "CARGO_REGISTRIES_PRIVATE_TOKEN": "must-not-be-recorded",
    }
    command = ["uv", "build", "--wheel", "--python", "/actual/python", "original.tar.gz"]
    receipt = module.capture(env, owner, tmp_path / "build", command)
    assert receipt["command"] == command
    assert receipt["environment"]["RUSTC_WRAPPER"] == "/configured/sccache"
    assert (
        receipt["environment"]["CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER"]
        == "/configured/workspace-wrapper"
    )
    assert "CARGO_REGISTRIES_PRIVATE_TOKEN" not in receipt["environment"]
    assert (
        receipt["cargo_configs"][str(owner / ".cargo/config.toml")]["settings"]["build"][
            "rustc-wrapper"
        ]
        == "sccache"
    )
    (owner / ".cargo/config.toml").write_text('[build]\nrustc-wrapper="changed-wrapper"\n')
    assert module.capture(env, owner, tmp_path / "build", command) != receipt

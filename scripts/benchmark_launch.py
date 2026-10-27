"""Record the selected native build tools and launch configuration without credentials."""

import hashlib
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ENVIRONMENT_NAMES = {
    "AR",
    "ARFLAGS",
    "CC",
    "CXX",
    "CFLAGS",
    "CPPFLAGS",
    "CXXFLAGS",
    "LDFLAGS",
    "MACOSX_DEPLOYMENT_TARGET",
    "SDKROOT",
    "CARGO_HOME",
    "CARGO_INCREMENTAL",
    "CARGO_ENCODED_RUSTFLAGS",
    "RUSTC",
    "RUSTC_WRAPPER",
    "RUSTC_WORKSPACE_WRAPPER",
    "RUSTUP_TOOLCHAIN",
    "RUSTFLAGS",
    "RUSTDOC",
    "UV_NO_CONFIG",
    "UV_PYTHON",
}
BUILD_SETTINGS = {
    "rustc",
    "rustc-wrapper",
    "rustc-workspace-wrapper",
    "rustflags",
    "target",
    "target-dir",
    "build-dir",
    "incremental",
}
TARGET_SETTINGS = {"rustflags", "rustdocflags", "linker", "runner"}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tools(env):
    result = {
        "python": {
            "binary": str(Path(sys.executable).resolve()),
            "sha256": digest(Path(sys.executable).resolve()),
            "version": sys.version,
        }
    }
    for program in ("uv", "rustc", "cargo"):
        launcher = shutil.which(program, path=env["PATH"])
        if launcher is None:
            raise FileNotFoundError(program)
        # Preserve argv[0] for rustup's compiler/Cargo shims, including symlinks.
        launcher = Path(launcher).absolute()
        if program == "uv":
            binary = launcher
            command = [str(launcher), "--version"]
        else:
            binary = Path(
                subprocess.check_output(
                    ["rustup", "which", "--toolchain", env["RUSTUP_TOOLCHAIN"], program],
                    env=env,
                    text=True,
                ).strip()
            ).resolve(strict=True)
            command = [str(launcher), "+" + env["RUSTUP_TOOLCHAIN"], "-vV"]
        result[program] = {
            "launcher": str(launcher),
            "launcher_sha256": digest(launcher),
            "binary": str(binary),
            "sha256": digest(binary),
            "command": command,
            "version": subprocess.check_output(command, env=env, text=True).strip(),
        }
    return result


def configurations(owner, isolated_output, env):
    roots = {owner, isolated_output, *isolated_output.parents}
    home = Path(env.get("CARGO_HOME", str(Path(env["HOME"]) / ".cargo")))
    # bounded: the build's ancestor configuration files and one Cargo home.
    paths = {root / ".cargo" / name for root in roots for name in ("config", "config.toml")}
    paths.update(home / name for name in ("config", "config.toml"))
    result = {}
    for path in sorted(paths):
        if not path.is_file():
            continue
        config = tomllib.loads(path.read_text())
        settings = {
            "build": {
                key: value
                for key, value in config.get("build", {}).items()
                if key in BUILD_SETTINGS
            },
            "target": {
                target: {key: value for key, value in values.items() if key in TARGET_SETTINGS}
                for target, values in config.get("target", {}).items()
            },
            "profile": config.get("profile", {}),
        }
        result[str(path)] = {"sha256": digest(path), "settings": settings}
    return result


def capture(env, owner, isolated_output, command):
    return {
        "command": list(map(str, command)),
        "environment": {
            name: value
            for name, value in sorted(env.items())
            if name in ENVIRONMENT_NAMES
            or name.startswith(("CARGO_BUILD_", "CARGO_PROFILE_", "CARGO_TARGET_", "PYO3_"))
        },
        "tools": tools(env),
        "cargo_configs": configurations(owner, isolated_output, env),
    }

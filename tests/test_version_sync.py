"""Release preparation must keep the uv lock current without dependency upgrades."""

import importlib.util
import re
import subprocess
from pathlib import Path


def test_version_bump_keeps_uv_lock_current(tmp_path):
    root = Path(__file__).parents[1]
    spec = importlib.util.spec_from_file_location("sync_version", root / "scripts/sync_version.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "version-regression"\nversion = "0.1.0"\nrequires-python = ">=3.11"\n'
    )
    subprocess.run(["uv", "lock", "--offline", "--project", str(tmp_path)], check=True)
    module.synchronize(tmp_path, "0.2.0")
    subprocess.run(["uv", "lock", "--check", "--offline", "--project", str(tmp_path)], check=True)


def test_real_project_version_bump_works_with_an_empty_uv_cache(tmp_path, monkeypatch):
    import shutil
    import tomllib

    root = Path(__file__).parents[1]
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(root / name, tmp_path / name)
    # Private paired checkouts override the provider during development. A
    # standalone release copy must resolve the unchanged declared dependency,
    # rather than search for an unrelated sibling below pytest's temp directory.
    project = tmp_path / "pyproject.toml"
    text = project.read_text()
    sources = tomllib.loads(text).get("tool", {}).get("uv", {}).get("sources", {})
    for name, source in sources.items():
        if source.get("editable") is True and source.get("path", "").startswith("../"):
            text, count = re.subn(
                rf"^{re.escape(name)} = \{{[^\n]+\}}\n", "", text, flags=re.MULTILINE
            )
            assert count == 1
    project.write_text(text)
    before = tomllib.loads((tmp_path / "uv.lock").read_text())
    spec = importlib.util.spec_from_file_location("sync_version", root / "scripts/sync_version.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setenv("UV_CACHE_DIR", str(tmp_path / "empty-cache"))
    module.synchronize(tmp_path, "0.0.999")
    subprocess.run(["uv", "lock", "--check", "--offline", "--project", str(tmp_path)], check=True)
    after = tomllib.loads((tmp_path / "uv.lock").read_text())

    def versions(lock):
        return {(p["name"], p["version"]) for p in lock["package"] if p["name"] != "pyshacl-turbo"}

    assert versions(before) == versions(after)

"""Execution companion authority is separate from the native owner's build peer."""

import copy
import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class AuthorityTests(unittest.TestCase):
    def test_current_bounded_requirement_selects_the_exact_locked_registry_peer(self):
        lock = tomllib.loads((ROOT / "uv.lock").read_text())
        expected = next(
            item["version"] for item in lock["package"] if item["name"] == "owlrl-turbo"
        )
        self.assertEqual(module("published_peers").execution_owl_version(ROOT), expected)

    def test_uv_rejects_a_requirement_that_excludes_the_locked_peer(self):
        manifest = (ROOT / "pyproject.toml").read_text()
        original = "owlrl-turbo>=0.2.0a1,<0.3"
        self.assertIn(original, manifest)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text(
                manifest.replace(original, "owlrl-turbo>=0.3,<0.4")
            )
            (root / "uv.lock").write_bytes((ROOT / "uv.lock").read_bytes())
            with self.assertRaisesRegex(ValueError, "Consumer lock differs"):
                module("published_peers").execution_owl_version(root)

    def context(self):
        old = {
            "source": "/build/owl-a3",
            "archive": "/build/a3.tar.gz",
            "sha256": "old",
            "wheel": "/build/a3.whl",
        }
        selected = {
            "source": "/execution/owl-alpha1",
            "archive": "/execution/a1.tar.gz",
            "sha256": "new",
            "wheel": "/execution/a1.whl",
        }
        return {
            "owner": Path("/native"),
            "acceptance": Path("/facade"),
            "wheel": Path("/facade.whl"),
            "output": Path("/out"),
            "receipt": {
                "execution_owlrl": selected,
                "provider": {
                    "source_archive": "/native.tar.gz",
                    "source_sha256": "native",
                    "collector_sha256": "collector",
                    "peers": {"owlrl": old, "yaml_test_dependency": {"authority": "/yaml.json"}},
                },
            },
        }

    def test_selected_execution_peer_reaches_existing_collector(self):
        context = self.context()
        before = copy.deepcopy(context)
        result = module("owner_driver").coverage_arguments(context)
        self.assertEqual(result.owlrl_source, Path("/execution/owl-alpha1"))
        self.assertEqual(result.owlrl_archive, Path("/execution/a1.tar.gz"))
        self.assertEqual(result.owlrl_wheel, Path("/execution/a1.whl"))
        self.assertEqual(result.owlrl_sha256, "new")
        self.assertEqual(context, before)

    def test_missing_execution_authority_never_falls_back(self):
        context = self.context()
        del context["receipt"]["execution_owlrl"]
        with self.assertRaises(KeyError):
            module("owner_driver").coverage_arguments(context)

    def test_benchmark_passes_execution_not_build_authority(self):
        benchmark = module("build_published_benchmark")
        benchmark.load = lambda name: SimpleNamespace(digest=lambda path: "facade-sha")
        context = self.context()
        provider = context["receipt"]["provider"]
        original = copy.deepcopy(provider)
        command = benchmark.builder_arguments(
            Path("/facade"),
            "revision",
            Path("/facade.whl"),
            provider,
            {"path": "/execution/a1.whl", "sha256": "execution-wheel"},
            Path("/out"),
            execution_owlrl=context["receipt"]["execution_owlrl"],
        )
        self.assertEqual(command[command.index("--owlrl-source") + 1], "/execution/owl-alpha1")
        self.assertEqual(command[command.index("--owlrl-archive") + 1], "/execution/a1.tar.gz")
        self.assertEqual(command[command.index("--owlrl-wheel") + 1], "/execution/a1.whl")
        self.assertEqual(provider, original)

    def test_selector_requests_distinct_original_and_keeps_owner(self):
        peers = module("published_peers")
        requests = []
        peers.execution_owl_version = lambda consumer: "0.2.0a1"

        def restore(project, version, output, *, owner):
            requests.append((project, version, output, owner))
            return {"source": "selected"}

        peers.original_peer = restore
        self.assertEqual(
            peers.execution_peer(Path("/facade"), Path("/native"), Path("/execution")),
            {"source": "selected"},
        )
        self.assertEqual(
            requests, [("owlrl-turbo", "0.2.0a1", Path("/execution"), Path("/native"))]
        )

    def test_selected_original_source_and_wheel_tampering_are_hard_errors(self):
        peers = module("published_peers")
        peer = {
            "archive": "/original.tar.gz",
            "source": "/source",
            "sha256": "archive-sha",
            "files": {"file": "original"},
            "wheel": "/original.whl",
            "wheel_sha256": "wheel-sha",
            "package_payload": {"owlrl_turbo/__init__.py": "original"},
        }
        current = {
            "files": peer["files"],
            "wheel_sha": "wheel-sha",
            "payload": peer["package_payload"],
        }
        peers.load = lambda name: (
            SimpleNamespace(verify_extracted=lambda *args, **kwargs: current["files"])
            if name == "provider_registry"
            else SimpleNamespace(digest=lambda path: current["wheel_sha"])
        )
        peers.load_companion = lambda owner: SimpleNamespace(
            verify_payload=lambda *args: current["payload"]
        )
        peers.verify_owl_peer(Path("/owner"), peer)
        for key, changed in (
            ("files", {"file": "changed"}),
            ("wheel_sha", "changed"),
            ("payload", {}),
        ):
            before = current[key]
            current[key] = changed
            with self.subTest(key=key), self.assertRaises(ValueError):
                peers.verify_owl_peer(Path("/owner"), peer)
            current[key] = before

    def requirement(self, requirements, *, source=None, binding=False, check_returncode=0):
        peers = module("published_peers")
        peers.load = lambda name: SimpleNamespace(
            VERSION=r"[0-9]+\.[0-9]+\.[0-9]+(?:a[0-9]+)?", PROJECTS={"owlrl-turbo"}
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            values = ",".join(repr(value) for value in requirements)
            (root / "pyproject.toml").write_text(
                "[project.optional-dependencies]\ntest=["
                + values
                + "]\n"
                + ('[tool.uv.sources]\nowlrl-turbo={path="../candidate"}\n' if binding else "")
            )
            source = source if source is not None else {"registry": "https://pypi.org/simple"}
            encoded = ",".join(f"{name}={value!r}" for name, value in source.items())
            (root / "uv.lock").write_text(
                '[[package]]\nname="owlrl-turbo"\nversion="0.2.0a1"\nsource={' + encoded + "}\n"
            )
            with patch.object(
                peers.subprocess,
                "run",
                return_value=SimpleNamespace(returncode=check_returncode, stderr="invalid lock"),
            ):
                return peers.execution_owl_version(root)

    def test_exact_consumer_test_authority(self):
        self.assertEqual(self.requirement(["pytest==9.1.1", "owlrl-turbo==0.2.0a1"]), "0.2.0a1")

    def test_missing_url_marker_extras_and_duplicate_rejected(self):
        for requirements in (
            [],
            ["owlrl-turbo @ file:///candidate.whl"],
            ["owlrl-turbo==0.2.0a1; python_version>'3'"],
            ["owlrl-turbo[test]==0.2.0a1"],
            ["owlrl-turbo==0.2.0a1"] * 2,
        ):
            with self.subTest(requirements=requirements), self.assertRaises(ValueError):
                self.requirement(requirements)

    def test_source_overrides_and_non_registry_locks_are_rejected(self):
        requirements = ["owlrl-turbo>=0.2.0a1,<0.3"]
        with self.assertRaises(ValueError):
            self.requirement(requirements, binding=True)
        for source in (
            {"path": "../candidate"},
            {"url": "https://example.org/candidate.whl"},
            {"registry": "https://example.org/simple"},
        ):
            with self.subTest(source=source), self.assertRaises(ValueError):
                self.requirement(requirements, source=source)
        with self.assertRaisesRegex(ValueError, "Consumer lock differs"):
            self.requirement(requirements, check_returncode=1)


if __name__ == "__main__":
    unittest.main()

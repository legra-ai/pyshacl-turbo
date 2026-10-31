"""Closed fresh-child operations and lossless complete proof transport."""

import gzip
import importlib.util
import io
import json
import platform
import sys
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "matched_worker_authority", Path(__file__).with_name("matched_graph_authority.py")
)
AUTHORITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUTHORITY)
SAMPLER = AUTHORITY.load("matched_graph_sampling")
PRODUCTS = {"rdflib_turbo", "owlrl_turbo", "pyshacl_turbo", "rdflib", "owlrl", "pyshacl"}


def write_proof(path, value):
    with (
        path.open("xb") as stream,
        gzip.GzipFile(fileobj=stream, mode="wb", mtime=0) as compressed,
        io.TextIOWrapper(compressed, encoding="utf-8") as text,
    ):
        json.dump(value, text)


def read_proof(path):
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def origins(backend):
    modules = {
        name: value.__file__
        for name, value in sys.modules.items()
        if name.split(".")[0] in PRODUCTS and getattr(value, "__file__", None)
    }
    if any(not Path(path).is_relative_to(sys.prefix) for path in modules.values()):
        raise RuntimeError("Runtime source imports are prohibited")
    loaded = {name.split(".")[0] for name in modules}
    forbidden = (
        {"rdflib_turbo", "owlrl_turbo", "pyshacl_turbo"}
        if backend == "reference"
        else {"owlrl", "pyshacl"}
    )
    if loaded & forbidden:
        raise RuntimeError("The timing child imported the other implementation")
    dsos = sorted({path for path in modules.values() if path.endswith((".so", ".pyd", ".dylib"))})
    if backend == "turbo":
        from rdflib_turbo import _native

        if dsos != [_native.__file__]:
            raise RuntimeError("Expected the sole selected native provider DSO")
    elif dsos:
        raise RuntimeError("Original child loaded an unexpected product DSO")
    return {"origins": modules, "native_sha256": {path: AUTHORITY.sha(Path(path)) for path in dsos}}


def execute(job, proof, entered):
    if sys.version_info[:3] != (3, 13, 16):
        raise RuntimeError("Matched benchmark requires CPython3.13.16")
    if job["backend"] not in {"reference", "turbo"}:
        raise ValueError("Unknown matched backend")
    if job["kind"] == "correctness":
        value = {
            "observation": SAMPLER.CONTRACT.correctness(
                job["backend"], job["width"], job["profile"], job["normalize"]
            )
        }
    elif job["kind"] == "sample":
        expected = read_proof(Path(job["oracle"]))["observation"]
        value = SAMPLER.sample(job["backend"], job["width"], job["profile"], expected)
        if value["peak_rss_bytes"] > 1280 * 1024 * 1024:
            raise RuntimeError("1280MiB absolute peak RSS limit exceeded")
    else:
        raise ValueError("Unknown matched worker operation")
    value["authority"] = {
        **origins(job["backend"]),
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "entry_perf_ns": entered,
    }
    write_proof(proof, value)
    return {
        "proof": proof.name,
        "sha256": AUTHORITY.sha(proof),
        "gate": value.get("gate"),
        "peak_rss_bytes": value.get("peak_rss_bytes"),
    }

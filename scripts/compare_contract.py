"""Measure direct public contracts in isolated, time-bounded processes.

No upstream redirection bridge or exception aliases are installed. Timings exclude
input construction and observation encoding, and are published only for equal
observations. The finite catalogue is not a percentage of all possible behavior.
"""

import argparse
import contextlib
import hashlib
import importlib
import io
import json
import platform
import random
import statistics
import subprocess
import sys
import tempfile
import time
import warnings
from collections import Counter, UserList
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

from rdflib import BNode, Dataset, Graph, URIRef
from rdflib.compare import to_isomorphic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from upstream_support.process_launch import Popen

PREFIXES = """@prefix ex: <urn:example:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
"""
DATA = "ex:a a ex:Person. ex:b a ex:Person; ex:p 1.\n"
SHAPES = "ex:S sh:targetNode ex:a; sh:path ex:p; sh:minCount 1."
RULES = """ex:First sh:targetClass ex:Person;
sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:first; sh:object true].
ex:Second sh:targetNode ex:b;
sh:rule [a sh:TripleRule; sh:subject sh:this; sh:predicate ex:second; sh:object true].
"""


def catalogue():
    cases = []

    def api(name, **options):
        cases.append({"id": name, "kind": "api", **options})

    for kind in ("graph", "dataset", "store", "text", "bytes"):
        for conforming in (False, True):
            api(
                f"validate/{kind}/{'conforming' if conforming else 'violation'}",
                input=kind,
                data=DATA + ("ex:a ex:p 1." if conforming else ""),
            )
    for kind in ("list", "tuple", "user-list"):
        for entrypoint in ("validate", "validate_each"):
            api(
                f"{entrypoint}/{kind}",
                input=kind,
                entrypoint=entrypoint,
                options={"multi_data_graphs_mode": "validate_each"}
                if entrypoint == "validate"
                else {},
            )
    for kind in ("empty-list", "graph", "text"):
        api(f"validate_each/reject-{kind}", input=kind, entrypoint="validate_each", error=True)
    for entrypoint in ("validate", "validate_each", "shacl_rules"):
        api(
            f"{entrypoint}/legacy-positional",
            entrypoint=entrypoint,
            input="list" if entrypoint == "validate_each" else "graph",
            positional=["legacy positional argument"],
        )
    for name, selection in (
        ("focus", {"focus_nodes": ["ex:a"]}),
        ("shape", {"use_shapes": ["ex:First"]}),
        ("untargeted", {"use_shapes": ["ex:First"], "focus_nodes": ["ex:untargeted"]}),
        ("override-target", {"use_shapes": ["ex:Second"], "focus_nodes": ["ex:a"]}),
    ):
        for entrypoint in ("validate", "shacl_rules"):
            api(
                f"{entrypoint}/rules-{name}",
                entrypoint=entrypoint,
                shapes=RULES,
                options={"inplace": True, "advanced": True, **selection},
            )
    for rdf_format in ("trig", "turtle", "nt", "json-ld", "xml"):
        api(
            f"shacl_rules/serialize-{rdf_format}",
            entrypoint="shacl_rules",
            shapes=RULES,
            options={
                "serialize_expanded_graph": True,
                "serialize_expanded_graph_format": rdf_format,
            },
            serialized=rdf_format,
        )
    for mode in ("rdfs", "owlrl", "both"):
        api(f"inference/{mode}/complete-closure", options={"inference": mode, "inplace": True})
    for name, shapes in (
        ("shape", "ex:S a sh:NodeShape; sh:path ex:p; sh:targetNode ex:a."),
        ("constraint", 'ex:S sh:targetNode ex:a; sh:path ex:p; sh:minCount "one".'),
        ("rule", "ex:S sh:targetNode ex:a; sh:rule [a sh:TripleRule; sh:subject sh:this]."),
    ):
        api(f"errors/{name}-load", shapes=shapes, options={"advanced": True}, error=True)
    api("reference/empty-document-autodetection", input="empty-document")
    for name in (
        "validate",
        "validate_each",
        "shacl_rules",
        "Validator",
        "RuleExpandRunner",
        "Shape",
        "ShapesGraph",
        "__version__",
    ):
        cases.append({"id": f"exports/{name}", "kind": "export", "name": name})
    for name, args in (
        ("shapes-alias", ["--shapes", "{shapes}"]),
        ("allow-infos-alias", ["--allow-infos"]),
        ("allow-warnings-alias", ["--allow-warnings"]),
        ("warning-short", ["-w"]),
        ("max-depth", ["--max-depth", "15"]),
        ("automatic-format", ["-df", "auto", "-sf", "auto"]),
        ("focus-whitespace", ["--focus", " ex:a , ex:b "]),
        ("shape-whitespace", ["--shape", " ex:S "]),
    ):
        cases.append({"id": f"cli/{name}", "kind": "cli", "args": args})
    cases.extend(
        [
            {
                "id": "cli/validate-each",
                "kind": "cli",
                "args": ["--validate-each", "{second}"],
                "human": True,
            },
            {
                "id": "cli/rules-selection",
                "kind": "cli",
                "rules": True,
                "args": ["--focus", "ex:a", "--shape", "ex:First"],
                "shapes": RULES,
            },
            {"id": "cli/no-input", "kind": "cli", "no_input": True},
            {"id": "cli/missing-input", "kind": "cli", "missing_input": True},
        ]
    )
    assert len({case["id"] for case in cases}) == len(cases)
    return cases


def rdf_snapshot(source):
    """Canonical reification retains quad scope and blank-node sharing.

    Unlike serializing N-Triples, this also represents generalized RDF literal
    subjects from the reference reasoner without discarding them.
    """
    graph = Graph()
    fields = [URIRef(f"urn:contract:{name}") for name in ("s", "p", "o", "g")]
    if isinstance(source, Dataset):
        rows = (
            (s, p, o, None if g == source.default_graph.identifier else g)
            for s, p, o, g in source.quads((None, None, None, None))
        )
    else:
        rows = ((*triple, None) for triple in source.triples((None, None, None)))
    count = 0
    for row in rows:
        node = BNode()
        for predicate, value in zip(fields, row):
            if value is not None:
                graph.add((node, predicate, value))
        count += 1
    return {"statements": count, "digest": format(to_isomorphic(graph).graph_digest(), "x")}


def graph(body):
    return Graph(identifier=URIRef("urn:contract:input")).parse(
        data=PREFIXES + body, format="turtle"
    )


def inputs(case):
    body = case.get("data", DATA)
    kind = case.get("input", "graph")
    if kind == "graph":
        return graph(body)
    if kind == "dataset":
        result = Dataset(default_union=True)
        result.graph(URIRef("urn:contract:named")).parse(data=PREFIXES + body, format="turtle")
        return result
    if kind == "store":
        from pyoxigraph import RdfFormat, Store

        result = Store()
        result.load(input=PREFIXES + body, format=RdfFormat.TURTLE)
        return result
    if kind in {"list", "tuple", "user-list"}:
        return {"list": list, "tuple": tuple, "user-list": UserList}[kind](
            [graph(body), graph(body + "ex:a ex:p 1.")]
        )
    if kind == "empty-list":
        return []
    if kind == "empty-document":
        return b"\n"
    return (PREFIXES + body).encode() if kind == "bytes" else PREFIXES + body


def mutation(data):
    if isinstance(data, Graph):
        return rdf_snapshot(data)
    if isinstance(data, (list, tuple, UserList)):
        return [mutation(item) for item in data]
    if type(data).__name__ == "Store":
        from pyoxigraph import RdfFormat

        return rdf_snapshot(
            Dataset().parse(data=data.dump(format=RdfFormat.N_QUADS), format="nquads")
        )
    return None


def exception(error):
    return {
        "class": type(error).__name__,
        "bases": [base.__name__ for base in type(error).__mro__[1:]],
        "message": str(error),
        "args_type": type(error.args).__name__,
        "args": list(map(str, error.args)),
    }


def observe_result(result, case):
    if isinstance(result, tuple):
        conforms, report, text = result
        return {
            "type": "tuple",
            "conforms": conforms,
            "text": text,
            "report": exception(report) if isinstance(report, Exception) else rdf_snapshot(report),
        }
    if isinstance(result, dict):
        return {
            "type": "dict",
            "items": [[key, observe_result(value, case)] for key, value in result.items()],
        }
    if isinstance(result, Graph):
        return {
            "type": "graph",
            "graph": rdf_snapshot(result),
            "context_aware": result.context_aware,
            "identifier_type": type(result.identifier).__name__,
            "identifier": str(result.identifier),
        }
    if case.get("serialized"):
        rdf_format = case["serialized"]
        result_graph = (
            Dataset(default_union=True) if rdf_format in {"trig", "nquads", "json-ld"} else Graph()
        )
        result_graph.parse(data=result, format=rdf_format)
        return {"type": type(result).__name__, "graph": rdf_snapshot(result_graph)}
    return {"type": type(result).__name__, "value": result}


def api_observation(engine, case):
    data = inputs(case)
    options = {"shacl_graph": graph(case.get("shapes", SHAPES)), **case.get("options", {})}
    if case.get("input") in {"text", "bytes"}:
        options["data_graph_format"] = "turtle"
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always", RuntimeWarning)
        started = time.perf_counter_ns()
        try:
            result = getattr(engine, case.get("entrypoint", "validate"))(
                data, *case.get("positional", []), **options
            )
        except Exception as error:
            if not case.get("error"):
                raise
            elapsed = time.perf_counter_ns() - started
            observation = {"error": exception(error)}
        else:
            elapsed = time.perf_counter_ns() - started
            if case.get("error"):
                raise RuntimeError("Expected an exception, but the call returned successfully")
            else:
                observation = observe_result(result, case)
    observation["mutation"] = mutation(data)
    observation["warnings"] = [
        {"class": item.category.__name__, "message": str(item.message)} for item in recorded
    ]
    return observation, elapsed


class Capture(io.StringIO):
    def close(self):
        # The reference CLI owns and closes stdout. Retain it for observation.
        pass


def cli_observation(engine, case):
    with tempfile.TemporaryDirectory(prefix="pyshacl-contract-") as directory:
        files = {
            name: str(Path(directory) / f"{name}.ttl") for name in ("data", "shapes", "second")
        }
        Path(files["data"]).write_text(PREFIXES + DATA)
        Path(files["shapes"]).write_text(PREFIXES + case.get("shapes", SHAPES))
        Path(files["second"]).write_text(PREFIXES + DATA + "ex:a ex:p 1.")
        arguments = [files["data"], "-s", files["shapes"]]
        extra = [arg.format(**files) for arg in case.get("args", [])]
        if files["second"] in extra:
            arguments.insert(1, files["second"])
            extra.remove(files["second"])
        if not case.get("human"):
            arguments += ["-f", "turtle"]
        arguments += extra
        if case.get("no_input"):
            arguments = []
        if case.get("missing_input"):
            arguments[0] += ".missing"
        out, err = Capture(), Capture()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            module = ".cli_rules" if case.get("rules") and engine.__name__ == "pyshacl" else ".cli"
            cli = importlib.import_module(engine.__name__ + module)
            if case.get("rules") and engine.__name__ == "pyshacl_turbo":
                arguments.append("--rules")
            sys.argv = [engine.__name__, *arguments]
            try:
                code = cli.main(arguments) if engine.__name__ == "pyshacl_turbo" else cli.main()
            except SystemExit as exit_status:
                code = exit_status.code
        observation = {"exit_code": code, "stderr": err.getvalue()}
        if case.get("no_input"):
            # The usage banner intentionally has different product names.
            observation["stderr"] = err.getvalue().splitlines()[0]
        output = out.getvalue()
        if output and not case.get("human") and code in (0, 1):
            observation["report"] = rdf_snapshot(Graph().parse(data=output, format="turtle"))
        else:
            observation["stdout"] = output
        return observation


def worker(engine_name, case, repeats):
    engine = importlib.import_module(engine_name)
    if (
        not engine.validate.__module__.startswith(engine_name + ".")
        and engine.validate.__module__ != engine_name
    ):
        raise RuntimeError("The direct audit refuses a redirected validation entrypoint")
    if engine_name == "pyshacl" and engine.__version__ != "0.40.1":
        raise RuntimeError("The comparison requires the pinned pySHACL 0.40.1")
    if case["kind"] == "export":
        return {"state": "ok", "observation": {"present": hasattr(engine, case["name"])}}
    if case["kind"] == "cli":
        return {"state": "ok", "observation": cli_observation(engine, case)}
    samples = []
    first = None
    for _ in range(repeats + 1):
        observation, elapsed = api_observation(engine, case)
        if first is None:
            first = observation  # Untimed warmup; input is rebuilt before every call.
        elif observation != first:
            raise RuntimeError("Repeated calls produced different observations")
        else:
            samples.append(elapsed)
    return {"state": "ok", "observation": first, "samples_ns": samples}


def run_process(command, timeout):
    with Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            return {"state": "timeout", "timeout_seconds": timeout}
        if process.returncode:
            return {"state": "crash", "exit_code": process.returncode, "stderr": stderr}
        try:
            return json.loads(stdout)
        except json.JSONDecodeError:
            return {
                "state": "error",
                "message": "Invalid worker JSON",
                "stdout": stdout,
                "stderr": stderr,
            }


def compare(reference, turbo):
    if reference["state"] != "ok":
        return {"status": "reference_" + reference["state"], "turbo_state": turbo["state"]}
    if turbo["state"] != "ok":
        return {"status": "turbo_" + turbo["state"]}
    expected, actual = reference["observation"], turbo["observation"]
    differences = sorted(
        key
        for key in expected.keys() | actual.keys()
        if key not in expected or key not in actual or expected[key] != actual[key]
    )
    if differences:
        return {"status": "different", "different_fields": differences}
    result = {"status": "equal"}
    if reference.get("samples_ns") and turbo.get("samples_ns") and "error" not in expected:
        result["speedup"] = statistics.median(reference["samples_ns"]) / statistics.median(
            turbo["samples_ns"]
        )
    return result


def check_baseline(rows, baseline):
    ids = [row["id"] for row in rows]
    if len(ids) != len(set(ids)) or set(ids) != set(baseline):
        raise RuntimeError("The direct contract inventory changed or contains duplicates")
    for row in rows:
        expected = baseline[row["id"]]
        if row["status"] not in ("equal", expected["status"]):
            raise RuntimeError(f"Direct contract regression: {row['id']} ({row['status']})")
        if row["status"] == "different" and not set(row["different_fields"]).issubset(
            expected["different_fields"]
        ):
            raise RuntimeError(f"New differing fields in direct contract: {row['id']}")
        if row.get("turbo_state") != expected.get("turbo_state") and row["status"] != "equal":
            raise RuntimeError(f"Changed Turbo execution state in direct contract: {row['id']}")


def source_fingerprint():
    digest = hashlib.sha256()
    for directory in ("python", "crates", "scripts", "vendor"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.suffix in {".py", ".rs", ".toml"}:
                digest.update(str(path.relative_to(ROOT)).encode())
                digest.update(path.read_bytes())
    for name in (
        "Cargo.lock",
        "Cargo.toml",
        "pyproject.toml",
        "requirements-test.lock",
        "rust-toolchain.toml",
    ):
        digest.update(name.encode())
        digest.update((ROOT / name).read_bytes())
    return digest.hexdigest()


def markdown(report):
    lines = [
        "# Direct pySHACL comparison",
        "",
        f"Reference: pySHACL {report['reference_version']}. Turbo: {report['turbo_version']}.",
        f"Measured: {report['measured_at']}; {report['build_kind']}.",
        f"Platform: {report['platform']}. Python: {report['python']}.",
        f"Source fingerprint: `{report['source_sha256']}`.",
        "",
        "Each row calls the actual public package without the upstream test bridge.",
        "RDF comparison preserves literal terms, graph scope and blank-node sharing;",
        "generated blank-node labels are ignored. Report text and warning text are exact.",
        "CLI RDF serialization is compared as RDF; usage banners compare their first error line.",
        "Export presence checks measure availability only, not class behavior.",
        "",
        "Timings are medians after an untimed warmup, excluding input construction and",
        "observation encoding. Every timed repetition must match. Speedups are shown only",
        "when all measured observations agree; they apply to these small fixtures only.",
        "Reference errors/timeouts remain separate and never count as compatibility passes.",
        "",
        f"Outcomes: {dict(report['summary'])}. This catalogue is not universal compatibility coverage.",
        "",
        "| Case | Outcome | Differences | Speedup |",
        "| --- | --- | --- | --- |",
    ]
    for row in report["cases"]:
        speed = f"{row['speedup']:.2f}×" if "speedup" in row else "—"
        lines.append(
            f"| {row['id']} | {row['status']} | {', '.join(row.get('different_fields', []))} | {speed} |"
        )
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=["pyshacl", "pyshacl_turbo"])
    parser.add_argument("--case")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/direct-contract.json")
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    if args.repeats < 1 or args.timeout <= 0:
        parser.error("repeats and timeout must be positive")
    cases = catalogue()
    if args.worker:
        case = next(case for case in cases if case["id"] == args.case)
        try:
            result = worker(args.worker, case, args.repeats)
        except Exception as error:  # noqa: BLE001 - retain unexpected engine errors in the audit
            result = {"state": "error", "exception": exception(error)}
        print(json.dumps(result))
        return
    randomizer = random.Random(20261011)
    rows = []
    for case in cases:
        engines = ["pyshacl", "pyshacl_turbo"]
        randomizer.shuffle(engines)
        observations = {}
        for engine in engines:
            observations[engine] = run_process(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--worker",
                    engine,
                    "--case",
                    case["id"],
                    "--repeats",
                    str(args.repeats),
                ],
                args.timeout,
            )
        row = {
            "id": case["id"],
            **compare(observations["pyshacl"], observations["pyshacl_turbo"]),
            **observations,
        }
        rows.append(row)
        print(f"{row['id']}: {row['status']}", flush=True)
    report = {
        "schema": 1,
        "reference_version": version("pyshacl"),
        "turbo_version": version("pyshacl-turbo"),
        "measured_at": datetime.now(UTC).isoformat(),
        "build_kind": "working-tree release build (see source and native binary hashes)",
        "platform": platform.platform(),
        "python": platform.python_version(),
        "source_sha256": source_fingerprint(),
        "native_binary_sha256": hashlib.sha256(
            Path(importlib.import_module("pyshacl_turbo._native").__file__).read_bytes()
        ).hexdigest(),
        "repeats": args.repeats,
        "timeout_seconds": args.timeout,
        "summary": dict(Counter(row["status"] for row in rows)),
        "unmeasured": [
            "unchanged pyshacl imports and command names",
            "public class behavior",
            "remote SPARQL endpoints",
            "HTTP server",
            "SHACL-JS (planned)",
            "complete inference/regex/datatype/AF feature space",
            "private motivating workload",
        ],
        "cases": rows,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    args.output.with_suffix(".md").write_text(markdown(report))
    if args.baseline:
        baseline = json.loads(args.baseline.read_text())
        check_baseline(rows, {row["id"]: row for row in baseline["cases"]})


if __name__ == "__main__":
    main()

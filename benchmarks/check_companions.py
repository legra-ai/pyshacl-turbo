"""Gate recorded RDF observations and previously equal cases, never timings."""

import argparse
import hashlib
import json


def without_text(observation):
    value = dict(observation)
    if "report" in value:
        value["report"] = {k: v for k, v in value["report"].items() if k != "text"}
    return value


def fingerprint(observation):
    encoded = json.dumps(without_text(observation), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def check(report, baseline):
    if "error" in report:
        raise RuntimeError(f"Benchmark failed: {report['error']}")
    sizes = {run["nodes"] for run in report["runs"]}
    if not sizes:
        raise RuntimeError("Empty benchmark inventory")
    actual = {}
    for run in report["runs"]:
        key = f"{run['operation']}/{run['nodes']}"
        if key in actual:
            raise RuntimeError(f"Duplicate benchmark case: {key}")
        actual[key] = run
    expected = {
        key: value
        for key, value in baseline["cases"].items()
        if int(key.rsplit("/", 1)[1]) in sizes
    }
    if actual.keys() != expected.keys():
        raise RuntimeError(
            f"Benchmark inventory changed: missing={sorted(expected.keys() - actual.keys())}, extra={sorted(actual.keys() - expected.keys())}"
        )
    for key, run in actual.items():
        recorded = expected[key]
        if run["backends"].keys() != recorded["backends"].keys():
            raise RuntimeError(f"Backend inventory changed: {key}")
        if recorded["comparison"] == "equal" and run.get("comparison", {}).get("status") != "equal":
            raise RuntimeError(f"Previously equal case lost full equality: {key}")
        for name, backend in run["backends"].items():
            observations = backend["observations"] + [
                sample["observation"] for sample in backend["memory_samples"]
            ]
            if not observations or any(
                fingerprint(value) != recorded["backends"][name] for value in observations
            ):
                raise RuntimeError(f"RDF observation changed: {key}/{name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True)
    parser.add_argument("--baseline", required=True)
    args = parser.parse_args()
    with open(args.report) as source:
        report = json.load(source)
    with open(args.baseline) as source:
        baseline = json.load(source)
    check(report, baseline)
    print(
        f"Checked {len(report['runs'])} cases against the recorded RDF baseline; known differences remain differences"
    )


if __name__ == "__main__":
    main()

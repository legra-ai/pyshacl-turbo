"""Fresh-process complete reports for bounded generic cycles, without global caches."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from rdflib import Graph
from rdflib.compare import isomorphic


def observe(engine, case, leading, prefix):
    from importlib import import_module

    data = Graph()
    data.bind(prefix, "urn:example:")
    source = """@prefix ex:<urn:example:>. @prefix sh:<http://www.w3.org/ns/shacl#>.
    ex:S sh:targetNode ex:s;sh:property [sh:path ex:required;sh:minCount 1;ex:note _:head].
    """
    if case == "shared-dag":
        source += """_:head ex:a _:shared;ex:z _:chain0.
        _:chain0 ex:next _:chain1. _:chain1 ex:next _:shared.
        _:shared ex:next _:tail0. _:tail0 ex:next _:tail1. _:tail1 ex:value "end"."""
    else:
        for index in range(leading):
            here = "head" if index == 0 else f"lead{index}"
            source += f"_:{here} ex:next _:lead{index + 1}. "
        head = "head" if leading == 0 else f"lead{leading}"
        source += (
            f"_:{head} ex:back _:{head}."
            if case == "self"
            else f"_:{head} ex:back _:other. _:other ex:back _:{head}."
        )
    shapes = Graph().parse(data=source.replace("ex:", f"{prefix}:"), format="turtle")
    before = set(data), set(shapes), tuple(data.namespaces()), tuple(shapes.namespaces())
    implementation = import_module("pyshacl" if engine == "reference" else "pyshacl_turbo")
    result = []
    for _ in range(2):
        conforms, report, text = implementation.validate(data, shacl_graph=shapes)
        result.append({"conforms": conforms, "graph": report.serialize(format="nt"), "text": text})
    if engine == "candidate":
        assert before == (set(data), set(shapes), tuple(data.namespaces()), tuple(shapes.namespaces()))
    return result


@pytest.mark.parametrize("case", ["self", "two-node", "shared-dag"])
@pytest.mark.parametrize("leading", [0, 1, 3])
@pytest.mark.parametrize("prefix", ["ex", "bound"])
def test_generic_cycle_complete_report_matches_fresh_reference(case, leading, prefix):
    observations = []
    for engine in ("reference", "candidate"):
        process = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), engine, case, str(leading), prefix],
            text=True, capture_output=True, check=True, timeout=30,
        )
        observations.append(json.loads(process.stdout))
    for expected, actual in zip(*observations, strict=True):
        assert actual["conforms"] == expected["conforms"] == False
        assert isomorphic(
            Graph().parse(data=actual["graph"], format="nt"),
            Graph().parse(data=expected["graph"], format="nt"),
        )
        assert actual["text"] == expected["text"]


if __name__ == "__main__":
    print(json.dumps(observe(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])))

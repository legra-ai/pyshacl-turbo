"""Native SHACL execution does not load the unused Python SPARQL interpreter."""

import subprocess
import sys


def test_native_sparql_validation_does_not_import_rdflib_query_backend():
    code = '''
import sys
import pyshacl_turbo as turbo
from rdflib import Graph, Literal, URIRef
data = Graph()
data.add((URIRef("urn:s"), URIRef("urn:p"), Literal("value")))
shapes = """@prefix sh: <http://www.w3.org/ns/shacl#> .
<urn:S> sh:targetNode <urn:s>; sh:sparql [sh:select
  "SELECT $this WHERE { $this <urn:p> ?value }"] ."""
assert not turbo.validate(data, shacl_graph=shapes)[0]
assert "rdflib.plugins.sparql.operators" not in sys.modules
'''
    result = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr

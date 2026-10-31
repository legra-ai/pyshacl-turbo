"""RDF boundary contracts, including real local HTTP responses and graph identity."""

import io
import nturl2path
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import PureWindowsPath

import pyoxigraph as ox
import pytest
from pyshacl_turbo import rdf
from rdflib import BNode, Dataset, Graph, Literal, URIRef
from rdflib.namespace import OWL
from rdflib.plugins.parsers.ntriples import ParseError
from test_compatibility import EX, graph


@pytest.mark.parametrize("name", ["space file.ttl", "unicode-Ω.ttl", "literal%20.ttl"])
def test_file_uri_names_preserve_encoding_and_literal_words(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b'\xef\xbb\xbf<#s> <urn:p> "01"^^<http://www.w3.org/2001/XMLSchema#integer>.')
    result = rdf.load_from_source(path.as_uri())
    value = result.value(URIRef(path.as_uri() + "#s"), URIRef("urn:p"))
    assert str(value) == "01"
    assert value.datatype == URIRef("http://www.w3.org/2001/XMLSchema#integer")


def test_document_decodes_windows_file_uri_before_resolving_and_reading(monkeypatch):
    expected = PureWindowsPath("C:/fixture root/unicode-Ω%20.ttl")
    calls = []

    class WindowsPath(PureWindowsPath):
        def resolve(self, *, strict):
            assert strict is True
            assert self == expected
            calls.append("resolve")
            return self

        def read_bytes(self):
            assert self == expected
            calls.append("read")
            return b'\xef\xbb\xbf<#s> <urn:p> "word".'

    monkeypatch.setattr(rdf, "Path", WindowsPath)
    monkeypatch.setattr(rdf, "url2pathname", nturl2path.url2pathname, raising=False)
    text, rdf_format, base = rdf._document(expected.as_uri(), None)
    assert text == '<#s> <urn:p> "word".'
    assert rdf_format == "turtle"
    assert base == expected.as_uri()
    assert calls == ["resolve", "read"]


@pytest.fixture
def documents():
    responses = {}
    requests = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append((self.path, self.headers.get("Accept")))
            status, headers, body = responses[self.path]
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.01})
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", responses, requests
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_http_redirect_uses_final_document_base_and_requests_rdf(documents):
    base, responses, requests = documents
    responses["/redirect"] = (302, {"Location": "/final/data"}, "")
    responses["/final/data"] = (200, {"Content-Type": "text/turtle"}, '<#s> <urn:p> "ok".')
    result = rdf.load_from_source(base + "/redirect")
    assert (URIRef(base + "/final/data#s"), URIRef("urn:p"), Literal("ok")) in result
    assert all("text/turtle" in accept for _, accept in requests)


@pytest.mark.parametrize(
    "media, path, fmt",
    [
        ("application/n-triples", "/data", None),
        ("application/octet-stream", "/data.nt", None),
        ("application/rdf+xml", "/data", "nt"),
    ],
)
def test_http_format_selection_uses_explicit_format_then_mime_then_extension(
    documents, media, path, fmt
):
    base, responses, _ = documents
    responses[path] = (200, {"Content-Type": media}, f'<{EX.s}> <{EX.p}> "ok" .')
    assert rdf.load_from_source(base + path, rdf_format=fmt).value(EX.s, EX.p) == Literal("ok")


def test_file_objects_keep_relative_iris_and_utf8_bom(tmp_path):
    path = tmp_path / "data with spaces.ttl"
    path.write_bytes(b'\xef\xbb\xbf<#s> <urn:p> "ok".')
    with path.open("rb") as source:
        loaded = rdf.load_from_source(source)
    assert (URIRef(path.as_uri() + "#s"), URIRef("urn:p"), Literal("ok")) in loaded
    assert set(rdf.load_from_source(path.as_uri())) == set(loaded)
    assert rdf.load_from_source(io.StringIO('<urn:s> <urn:p> "ok".')).value(
        URIRef("urn:s"), URIRef("urn:p")
    ) == Literal("ok")


@pytest.mark.parametrize("fmt", ["xml", "json-ld"])
def test_inline_documents_detect_xml_and_jsonld(fmt):
    original = graph('ex:s ex:p "ok".')
    assert set(rdf.load_from_source(original.serialize(format=fmt))) == set(original)


def test_loader_rejects_invalid_sources_options_and_import_targets():
    with pytest.raises(TypeError, match="Expected an RDF"):
        rdf.load_from_source(42)
    with pytest.raises(TypeError, match="Unsupported loader options: invalid"):
        rdf.load_from_source(graph(""), invalid=True)
    source = graph("")
    source.add((EX.ontology, OWL.imports, Literal("not an IRI")))
    with pytest.raises(TypeError, match="owl:imports must name an IRI"):
        rdf.load_from_source(source, do_owl_imports=True)


@pytest.mark.parametrize("suffix", ["invalid .", '"ok" . trailing'])
def test_native_output_decoder_rejects_invalid_terms_and_trailing_content(suffix):
    with pytest.raises(ParseError, match="Invalid line"):
        rdf.decode(f"<urn:s> <urn:p> {suffix}")


def test_native_output_decoder_accepts_comments_and_blank_lines():
    result = rdf.decode('\n # comment\n<urn:s> <urn:p> "ok" .\n')
    assert list(result) == [(URIRef("urn:s"), URIRef("urn:p"), Literal("ok"))]


def test_input_snapshot_can_be_loaded_and_flattened_without_losing_blank_node_identity():
    source = Dataset(default_union=True)
    node, context = BNode("object"), BNode("context")
    source.graph(context).add((EX.s, EX.p, node))
    snapshot = rdf.input_graph(source)
    assert snapshot.blank_nodes[str(context)] == context
    decoded = rdf.load_from_source(snapshot)
    assert (EX.s, EX.p, node) in decoded.graph(context)
    flat = rdf.input_graph(snapshot, flatten=True)
    assert not rdf.load_from_source(flat).context_aware
    assert set(rdf.load_from_source(flat)) == {(EX.s, EX.p, node)}


def test_native_store_snapshot_load_preserves_explicit_string_types():
    source = ox.Store()
    source.load(input=f'<{EX.s}> <{EX.p}> "ok" .', format=ox.RdfFormat.N_TRIPLES)
    snapshot = rdf.input_graph(source)
    loaded = rdf.load_from_source(snapshot)
    assert loaded.value(EX.s, EX.p).datatype == URIRef("http://www.w3.org/2001/XMLSchema#string")
    with pytest.raises(ValueError, match="original input snapshot"):
        rdf.commit_serialized(source, snapshot.source)
    assert len(source) == 1


def test_loader_can_merge_dataset_union_into_an_existing_graph():
    source = Dataset(default_union=True)
    source.graph(EX.named).add((EX.s, EX.p, Literal("new")))
    target = graph('ex:existing ex:p "keep".')
    result = rdf.load_from_source(source, g=target)
    assert result is target
    assert set(target.triples((None, None, None))) == {
        (EX.s, EX.p, Literal("new")),
        (EX.existing, EX.p, Literal("keep")),
    }


@pytest.mark.parametrize("populated", [False, True])
def test_dataset_snapshot_handles_empty_contexts(populated):
    source = Dataset(default_union=True)
    source.graph(EX.empty)
    if populated:
        source.graph(EX.populated).add((EX.s, EX.p, Literal("line one\nline two")))
    snapshot = rdf.input_graph(source)
    decoded = rdf.load_from_source(snapshot, multigraph=True)
    assert set(decoded.quads()) == set(source.quads())


@pytest.mark.parametrize("dataset", [False, True])
def test_copy_graph_is_independent_and_retains_namespaces_and_contexts(dataset):
    source = Dataset(default_union=True) if dataset else Graph()
    source.bind("ex", EX)
    source.add((EX.s, EX.p, Literal("default")))
    if dataset:
        source.graph(EX.named).add((EX.s, EX.p, Literal("named")))
    copied = rdf.copy_graph(source)
    assert copied is not source
    assert dict(copied.namespaces())["ex"] == URIRef(EX)
    assert set(copied) == set(source)
    if dataset:
        assert set(copied.graph(EX.named)) == set(source.graph(EX.named))
        assert set(copied.default_graph) == set(source.default_graph)
    copied.add((EX.new, EX.p, Literal("change")))
    assert (EX.new, EX.p, None) not in source


@pytest.mark.parametrize("source_dataset", [False, True])
@pytest.mark.parametrize("target_dataset", [False, True])
def test_graph_merge_preserves_named_contexts_when_available(source_dataset, target_dataset):
    source = Dataset(default_union=True) if source_dataset else Graph()
    target = Dataset(default_union=True) if target_dataset else Graph()
    context = source.graph(EX.named) if source_dataset else source
    context.add((EX.s, EX.p, Literal("new")))
    target.add((EX.existing, EX.p, Literal("keep")))
    assert rdf.merge_graph(target, source) is target
    assert set(target.triples((None, None, None))) == {
        (EX.s, EX.p, Literal("new")),
        (EX.existing, EX.p, Literal("keep")),
    }
    if target_dataset:
        destination = target.graph(EX.named) if source_dataset else target.default_graph
        assert (EX.s, EX.p, Literal("new")) in destination

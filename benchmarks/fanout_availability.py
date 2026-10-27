"""Closed observer authority, distinct from the unchanged pipeline contract."""

SCHEMA = "literal-inplace-owlrl-v1"
NATIVE = ("rdflib-turbo", "owlrl-turbo", "pyshacl-turbo")
REFERENCE = ("rdflib", "owlrl", "pyshacl")
HISTORICAL = ("0.1.0a2", "0.1.0a2", "0.2.4")


def public_contract(native):
    """Inspect the actual public route; semantic validation remains mandatory."""
    if native:
        from owlrl_turbo import expand
        from rdflib_turbo import Dataset

        owner, invoke, export = Dataset, expand, getattr(Dataset, "to_rdflib", None)
    else:
        from owlrl import DeductiveClosure
        from rdflib import Graph

        owner, invoke, export = Graph, DeductiveClosure.expand, Graph.triples
    return {
        "schema": SCHEMA,
        "route": "native" if native else "reference",
        "namespace_attribute_absent": not hasattr(owner, "namespaces"),
        "apis": {
            "parse": callable(getattr(owner, "parse", None)),
            "namespaces": callable(getattr(owner, "namespaces", None)),
            "export": callable(export),
            "invoke": callable(invoke),
        },
    }


def prepare(identity, backend):
    """A known exclusion is decided before invocation, never after failure."""
    if backend not in {"reference", "turbo", "turbo_shared"}:
        raise RuntimeError("Unknown closed observer backend")
    native = backend != "reference"
    contract = identity.get("fanout_observer", {})
    if contract.get("schema") != SCHEMA or contract.get("route") != (
        "native" if native else "reference"
    ):
        raise RuntimeError("Unknown or contradictory observer contract")
    names = NATIVE if native else REFERENCE
    packages = identity.get("packages", {})
    if any(not packages.get(name, {}).get("version") for name in names):
        raise RuntimeError("Missing resolved observer versions")
    versions = {name: packages[name]["version"] for name in names}
    payload = {name: packages[name].get("payload_sha256") for name in names}
    lock = identity.get("uv_lock_sha256")
    if not lock or any(not value for value in payload.values()):
        raise RuntimeError("Missing observer lock/payload authority")
    apis = contract.get("apis", {})
    if set(apis) != {"parse", "namespaces", "export", "invoke"} or any(
        type(value) is not bool for value in apis.values()
    ):
        raise RuntimeError("Malformed public observer API proof")
    result = {
        "schema": SCHEMA,
        "status": "contract_pending",
        "versions": versions,
        "uv_lock_sha256": lock,
        "payload_sha256": payload,
    }
    if native and tuple(versions.values()) == HISTORICAL:
        if contract.get("namespace_attribute_absent") is not True or apis != {
            "parse": True,
            "namespaces": False,
            "export": True,
            "invoke": True,
        }:
            raise RuntimeError("Known a2 public API differs from recorded absence")
        result.update(
            status="not_measured_observer_unavailable",
            reason="Published a2 Dataset.namespaces() public API is absent; inference is not classified as failed",
        )
    elif not all(apis.values()):
        raise RuntimeError("Missing required public observer API")
    return result


def measured(row, environments):
    """Only complete validated arms may participate in any comparison."""
    if row["contract"] == "pipeline":
        return environments
    if row["contract"] != "inference":
        raise RuntimeError("Unknown job observation contract")
    decisions = row.get("availability", {})
    if set(decisions) != {env["id"] for env in environments}:
        raise RuntimeError("Missing or foreign observer availability")
    selected = []
    for env in environments:
        entry = decisions[env["id"]]
        if entry.get("schema") != SCHEMA:
            raise RuntimeError("Unknown observer availability schema")
        if entry.get("status") == "measured_validated":
            if env["id"] not in row["environments"]:
                raise RuntimeError("Missing actual validated measurement")
            selected.append(env)
        elif entry.get("status") == "not_measured_observer_unavailable":
            if not entry.get("reason") or env["id"] in row["environments"]:
                raise RuntimeError("Excluded observer has missing reason or fake output")
        else:
            raise RuntimeError("Unknown or unvalidated observer availability status")
    return selected

"""Normalize public pySHACL inference options before native execution."""

from .errors import ReportableRuntimeError


def inference_mode(value):
    if not value or value == "none":
        return None
    if value in ("rdfs", "owlrl", "both"):
        return value
    if value in ("all", "rdfsowlrl"):
        return "both"
    raise ReportableRuntimeError(f"Don't know how to do '{value}' type inferencing.")

"""Validate sparse typed SH.value occurrences before constructing report terms."""

from rdflib.namespace import RDF, SH, XSD


def boolean_occurrences(records, quads, entries):
    def iri(index, value):
        return (
            type(index) is int
            and 0 <= index < len(records)
            and tuple(records[index]) == (0, str(value), None, None)
        )

    results = {(s, g) for s, p, o, g in quads if iri(p, RDF.type) and iri(o, SH.ValidationResult)}
    result = {}
    for entry in entries:
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError("Invalid Boolean report occurrence")
        index, code = entry
        if type(index) is not int or not 0 <= index < len(quads):
            raise ValueError("Invalid Boolean report quad index")
        if type(code) is not int or not 1 <= code <= 6 or index in result:
            raise ValueError("Invalid or duplicate Boolean report state")
        subject, predicate, value, context = quads[index]
        if (
            not iri(predicate, SH.value)
            or records[value][0] != 2
            or records[value][1] not in ("false", "true")
            or tuple(records[value][2:]) != (str(XSD.boolean), None)
            or (subject, context) not in results
        ):
            raise ValueError("Boolean occurrence is not a direct ValidationResult value")
        result[index] = (code >= 4, (None, False, True)[(code - 1) % 3])
    return result

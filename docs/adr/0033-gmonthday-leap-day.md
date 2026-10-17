# ADR 0033: Correct leap-day validation in the shared datatype parser

Status: Accepted

Native coverage tests exposed `xsd:gMonthDay` rejecting February 29, including
valid timezone suffixes. XSD permits this partial date without a year; its value
representation uses the leap-year reference 1972. The pinned oxsdatatypes parser
called its day validator with no year, selecting a non-leap February limit.

Vendor oxsdatatypes 0.2.3 at the same Oxigraph source revision as the existing
patches and validate gMonthDay against 1972 before constructing its value.
Retain the original parser for SHACL datatype validation and all other native
consumers. Ordinary date and timezone validation remain shared and unchanged.

Keep source revision/archive checksum, upstream license texts and a patch note.
Run the upstream datatype tests and a leap-day regression in required CI. Test
valid leap-day forms, malformed calendar dates, timezone limits and ordinary
non-leap-year rejection through the public SHACL API as well.

Specification: https://www.w3.org/TR/xmlschema11-2/#gMonthDay.

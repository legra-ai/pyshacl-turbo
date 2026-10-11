"""Command-line I/O for the native validator and rule runner."""

import argparse
import logging
import sys
from contextlib import ExitStack
from importlib.metadata import version

from rdflib import Dataset, Graph
from rdflib.namespace import SH

from . import shacl_rules, validate, validate_each


def table(headers, rows):
    def split(value):
        text = str(value)
        return [text[i : i + 25] for i in range(0, len(text), 25)] or [""]

    cells = [[split(value) for value in row] for row in [headers, *rows]]
    widths = [max(len(line) for row in cells for line in row[i]) for i in range(len(headers))]
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    result = [border]
    for index, row in enumerate(cells):
        for line in range(max(map(len, row))):
            result.append(
                "| "
                + " | ".join(
                    (column[line] if line < len(column) else "").ljust(width)
                    for column, width in zip(row, widths)
                )
                + " |"
            )
        if index == 0:
            result.append(border)
    result.append(border)
    return "\n".join(result) + "\n"


def report_table(conforms, report):
    output = table(["Conforms"], [[conforms]])
    if conforms:
        return output
    rows = []
    fields = [
        SH.resultSeverity,
        SH.focusNode,
        SH.resultPath,
        SH.resultMessage,
        SH.sourceConstraintComponent,
        SH.sourceShape,
        SH.value,
    ]
    for index, result in enumerate(report.objects(None, SH.result), 1):
        values = [
            str(report.value(result, predicate) or "-").replace(str(SH), "") for predicate in fields
        ]
        rows.extend([[index, *values], [""] * 8])
    return (
        output
        + "\n"
        + table(
            [
                "No.",
                "Severity",
                "Focus Node",
                "Result Path",
                "Message",
                "Component",
                "Shape",
                "Value",
            ],
            rows,
        )
    )


def serialize_graph(graph, rdf_format):
    if rdf_format in {"trig", "nquads"} and not graph.context_aware:
        dataset = Dataset()
        dataset.default_graph += graph
        for prefix, namespace in graph.namespaces():
            dataset.bind(prefix, namespace)
        graph = dataset
    return graph.serialize(format=rdf_format)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pyshacl-turbo")
    parser.add_argument("data", nargs="*")
    parser.add_argument("-s", "--shapes", "--shacl", dest="shacl_graph")
    parser.add_argument("-e", "--ont-graph", dest="ont_graph")
    parser.add_argument(
        "-i", "--inference", choices=["none", "rdfs", "owlrl", "both"], default="none"
    )
    parser.add_argument("-a", "--advanced", action="store_true")
    parser.add_argument("-m", "--metashacl", dest="meta_shacl", action="store_true")
    parser.add_argument("-j", "--js", action="store_true")
    parser.add_argument("-im", "--imports", dest="do_owl_imports", action="store_true")
    parser.add_argument("-it", "--iterate-rules", action="store_true")
    parser.add_argument("--abort", dest="abort_on_first", action="store_true")
    parser.add_argument("--allow-info", "--allow-infos", dest="allow_infos", action="store_true")
    parser.add_argument(
        "-w", "--allow-warning", "--allow-warnings", dest="allow_warnings", action="store_true"
    )
    parser.add_argument("--max-depth", dest="max_validation_depth", type=int)
    parser.add_argument("--validate-each", action="store_true")
    parser.add_argument("--focus")
    parser.add_argument("--shape")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("--rules", action="store_true")
    parser.add_argument("-df", "--data-file-format", dest="data_graph_format")
    parser.add_argument("-sf", "--shacl-file-format", dest="shacl_graph_format")
    parser.add_argument("-ef", "--ont-file-format", dest="ont_graph_format")
    parser.add_argument(
        "-f",
        "--format",
        default="human",
        choices=["human", "table", "turtle", "trig", "xml", "json-ld", "nt", "n3", "nquads"],
    )
    parser.add_argument("-o", "--output")
    parser.add_argument("-V", "--version", action="version", version=version("pyshacl-turbo"))
    args = parser.parse_args(argv)
    if not args.data:
        print("Input Error. No DataGraph file or endpoint supplied.", file=sys.stderr)
        parser.print_usage(sys.stderr)
        return 1
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    options = {
        name: getattr(args, name)
        for name in [
            "shacl_graph",
            "ont_graph",
            "inference",
            "advanced",
            "js",
            "do_owl_imports",
            "iterate_rules",
            "data_graph_format",
            "shacl_graph_format",
            "ont_graph_format",
            "debug",
            "max_validation_depth",
        ]
    }
    for name in ("data_graph_format", "shacl_graph_format", "ont_graph_format"):
        if options[name] == "auto":
            options[name] = None
    options.update(
        focus_nodes=[name.strip() for name in args.focus.split(",")] if args.focus else None,
        use_shapes=[name.strip() for name in args.shape.split(",")] if args.shape else None,
    )
    with ExitStack() as files:
        try:
            data = [
                sys.stdin.buffer.read()
                if source == "-"
                else files.enter_context(open(source, "rb"))
                for source in args.data
            ]
        except FileNotFoundError:
            print("Input Error. DataGraph file not found.", file=sys.stderr)
            return 1
        except PermissionError:
            print("Input Error. DataGraph file not readable.", file=sys.stderr)
            return 1
        return _run(args, data, options)


def _validation_output(result, rdf_format):
    conforms, report, text = result
    if rdf_format == "table" and isinstance(report, Graph):
        return report_table(conforms, report)
    if rdf_format != "human" and isinstance(report, Graph):
        return serialize_graph(report, rdf_format)
    return text


def _run(args, inputs, options):
    data = inputs[0] if len(inputs) == 1 else inputs
    try:
        if args.rules:
            options["advanced"] = True
            report = shacl_rules(data, **options)
            output_format = args.format if args.format not in {"human", "table"} else "trig"
            text = serialize_graph(report, output_format)
            conforms = True
        else:
            options.update(
                {
                    name: getattr(args, name)
                    for name in ["meta_shacl", "abort_on_first", "allow_infos", "allow_warnings"]
                }
            )
            if args.validate_each:
                results = validate_each(inputs, **options)
                conforms = all(result[0] for result in results.values())
                text = "".join(
                    f"=== Validation result for {index} ===\n"
                    + _validation_output(result, args.format)
                    + "\n"
                    for index, result in results.items()
                )
            else:
                result = validate(data, **options)
                conforms = result[0]
                text = _validation_output(result, args.format)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as output:
                output.write(text)
        else:
            sys.stdout.write(text)
        return 0 if conforms else 1
    except NotImplementedError as error:
        print(error, file=sys.stderr)
        return 3
    except (ValueError, RuntimeError, OSError) as error:
        print(error, file=sys.stderr)
        return 2


def entrypoint():
    raise SystemExit(main())


def rules_entrypoint():
    raise SystemExit(main(["--rules", *sys.argv[1:]]))


if __name__ == "__main__":
    entrypoint()

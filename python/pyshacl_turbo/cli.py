"""Command-line I/O for the native validator and rule runner."""

import argparse
import logging
import sys
from importlib.metadata import version

from rdflib import Dataset, Graph
from rdflib.namespace import SH

from . import shacl_rules, validate


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


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pyshacl-turbo")
    parser.add_argument("data", nargs="+")
    parser.add_argument("-s", "--shacl", dest="shacl_graph")
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
    parser.add_argument("--allow-info", dest="allow_infos", action="store_true")
    parser.add_argument("--allow-warning", dest="allow_warnings", action="store_true")
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
    parser.add_argument("--version", action="version", version=version("pyshacl-turbo"))
    args = parser.parse_args(argv)
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
        ]
    }
    data = [sys.stdin.buffer.read() if source == "-" else source for source in args.data]
    data = data[0] if len(data) == 1 else data
    try:
        if args.rules:
            options["advanced"] = True
            report = shacl_rules(data, **options)
            output_format = args.format if args.format not in {"human", "table"} else "trig"
            if output_format in {"trig", "nquads"} and not report.context_aware:
                dataset = Dataset()
                dataset.default_graph += report
                report = dataset
            text = report.serialize(format=output_format)
            conforms = True
        else:
            options.update(
                {
                    name: getattr(args, name)
                    for name in ["meta_shacl", "abort_on_first", "allow_infos", "allow_warnings"]
                }
            )
            options.update(
                focus_nodes=args.focus.split(",") if args.focus else None,
                use_shapes=args.shape.split(",") if args.shape else None,
            )
            conforms, report, text = validate(data, **options)
            if args.format == "table" and isinstance(report, Graph):
                text = report_table(conforms, report)
            elif args.format != "human" and isinstance(report, Graph):
                text = report.serialize(format=args.format)
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

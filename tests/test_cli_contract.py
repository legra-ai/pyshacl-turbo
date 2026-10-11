"""CLI behavior compared with the pinned reference in fresh interpreters."""

import contextlib
import io
import subprocess
import sys

import pytest
from rdflib import Graph
from rdflib.compare import isomorphic
from test_public_contract import PREFIXES, RULE_SHAPES
from upstream_support.process_launch import Popen


def invoke(package, args):
    if package == "pyshacl_turbo":
        from pyshacl_turbo.cli import main

        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main(args)
            except SystemExit as status:
                code = status.code
        return code, out.getvalue(), err.getvalue()
    with Popen(
        [sys.executable, "-m", package, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        try:
            out, err = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise
        return process.returncode, out, err


@pytest.fixture
def files(tmp_path):
    data, shapes = tmp_path / "data.ttl", tmp_path / "shapes.ttl"
    data.write_text(PREFIXES + "ex:a a ex:Person. ex:b a ex:Person; ex:p 1.")
    shapes.write_text(PREFIXES + "ex:S sh:targetNode ex:a; sh:path ex:p; sh:minCount 1.")
    return data, shapes


@pytest.mark.parametrize(
    "extra",
    [
        ["--allow-infos"],
        ["--allow-warnings"],
        ["-w"],
        ["--max-depth", "15"],
        ["-df", "auto", "-sf", "auto"],
        ["--focus", " ex:a , ex:b "],
        ["--shape", " ex:S "],
    ],
)
def test_validation_cli_accepts_reference_options(files, extra):
    data, shapes = files
    arguments = [str(data), "-s", str(shapes), "-f", "turtle", *extra]
    expected, actual = [invoke(package, arguments) for package in ("pyshacl", "pyshacl_turbo")]
    assert expected[0] == 1
    assert actual[0] == expected[0], actual[2]
    assert isomorphic(
        Graph().parse(data=actual[1], format="turtle"),
        Graph().parse(data=expected[1], format="turtle"),
    )


def test_shapes_cli_alias(files):
    data, shapes = files
    args = [str(data), "--shapes", str(shapes), "-f", "turtle"]
    expected, actual = [invoke(package, args) for package in ("pyshacl", "pyshacl_turbo")]
    assert actual[0] == expected[0] == 1
    assert isomorphic(Graph().parse(data=actual[1]), Graph().parse(data=expected[1]))


def test_cli_rules_apply_focus_and_shape_selection(files):
    data, shapes = files
    shapes.write_text(PREFIXES + RULE_SHAPES)
    args = [
        str(data),
        "--rules",
        "-s",
        str(shapes),
        "--focus",
        " ex:a ",
        "--shape",
        " ex:First ",
        "-f",
        "turtle",
    ]
    expected = invoke("pyshacl.cli_rules", [arg for arg in args if arg != "--rules"])
    actual = invoke("pyshacl_turbo", args)
    assert actual[0] == expected[0] == 0
    assert isomorphic(Graph().parse(data=actual[1]), Graph().parse(data=expected[1]))


def test_cli_validate_each_reports_each_input_and_aggregates_exit_status(files, tmp_path):
    data, shapes = files
    second = tmp_path / "second.ttl"
    second.write_text(PREFIXES + "ex:a ex:p 1.")
    args = [str(data), str(second), "-s", str(shapes), "--validate-each"]
    expected, actual = [invoke(package, args) for package in ("pyshacl", "pyshacl_turbo")]
    assert actual[0] == expected[0] == 1
    for result in (actual, expected):
        assert "=== Validation result for 0 ===" in result[1]
        assert "=== Validation result for 1 ===" in result[1]
        assert result[1].count("Conforms: False") == 1
        assert result[1].count("Conforms: True") == 1


@pytest.mark.parametrize("arguments", [[], ["/does/not/exist.ttl"]])
def test_cli_input_errors_match_reference_exit_and_message(arguments):
    expected, actual = [invoke(package, arguments) for package in ("pyshacl", "pyshacl_turbo")]
    assert actual[0] == expected[0] == 1
    assert actual[2].splitlines()[0] == expected[2].splitlines()[0]


def test_cli_short_version_option():
    from importlib.metadata import version

    actual = invoke("pyshacl_turbo", ["-V"])
    assert actual[0] == 0
    assert version("pyshacl-turbo") in actual[1] + actual[2]

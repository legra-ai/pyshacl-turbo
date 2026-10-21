"""Public runner construction and state; SHACL execution remains native."""

from typing import Any, ClassVar

from ._report import ReportBuilder
from ._runner import Runner
from .pytypes import SHACLExecutor


class Validator(Runner):
    _defaults: ClassVar[dict[str, Any]] = {
        "debug": False,
        "advanced": False,
        "inference": "none",
        "inplace": False,
        "use_js": False,
        "iterate_rules": False,
        "abort_on_first": False,
        "allow_infos": False,
        "allow_warnings": False,
        "sparql_mode": False,
        "max_validation_depth": 15,
        "focus_nodes": None,
        "use_shapes": None,
    }

    @classmethod
    def create_validation_report(cls, sg, conforms, results):
        return ReportBuilder.build(sg, conforms, results)

    def make_executor(self):
        return SHACLExecutor(
            validator=self,
            advanced_mode=bool(self.options.get("advanced", False)),
            abort_on_first=bool(self.options.get("abort_on_first", False)),
            allow_infos=bool(self.options.get("allow_infos", False)),
            allow_warnings=bool(self.options.get("allow_warnings", False)),
            iterate_rules=bool(self.options.get("iterate_rules", False)),
            sparql_mode=bool(self.options.get("sparql_mode", False)),
            max_validation_depth=self.options.get("max_validation_depth", 15),
            focus_nodes=self.options.get("focus_nodes"),
            debug=self.debug,
        )

    def run(self):
        from . import validate

        target = self._prepare_target()
        options = {
            key: value
            for key, value in self.options.items()
            if key not in {"logger", "use_js", "sparql_mode", "inference", "inplace"}
        }
        return validate.__wrapped__(
            target.impl, shacl_graph=self.shacl_graph.graph, inplace=True, **options
        )

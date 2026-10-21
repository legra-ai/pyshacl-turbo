"""Rule expansion runner using the native compiled rule engine."""

from typing import Any, ClassVar

from .validator import Validator


class RuleExpandRunner(Validator):
    _defaults: ClassVar[dict[str, Any]] = {
        "debug": False,
        "inference": "none",
        "inplace": False,
        "use_js": False,
        "iterate_rules": False,
        "focus_nodes": None,
        "use_shapes": None,
    }

    def run(self):
        from . import shacl_rules

        target = self._prepare_target(rules=True)
        options = {
            key: value
            for key, value in self.options.items()
            if key not in {"logger", "use_js", "inference", "inplace", "advanced"}
        }
        options.setdefault("max_validation_depth", 999)
        shacl_rules(
            target.impl, shacl_graph=self.shacl_graph.graph, inplace=True, advanced=True, **options
        )
        return target

"""Ensure upstream Python subprocesses exercise turbo too."""

import importlib.abc
import importlib.machinery
import os
import sys

if os.environ.get("PYSHACL_TURBO_TEST_REDIRECT") == "1":

    class RedirectFinder(importlib.abc.MetaPathFinder):
        def find_spec(self, fullname, path=None, target=None):
            if fullname != "pyshacl":
                return None
            spec = importlib.machinery.PathFinder.find_spec(fullname, path)
            original = spec.loader.exec_module

            def execute(module):
                original(module)
                from redirect import install

                install()

            spec.loader.exec_module = execute
            return spec

    sys.meta_path.insert(0, RedirectFinder())

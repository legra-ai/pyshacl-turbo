"""Public exception and warning contracts without a pySHACL dependency."""


class ReportableRuntimeError(RuntimeError):
    def __init__(self, message):
        self.message = message

    @property
    def args(self):
        return [self.message]

    def __str__(self):
        return str(self.message)

    def __repr__(self):
        return f"ReportableRuntimeError: {self}"


class ValidationWarning(RuntimeWarning):
    pass


class ShapeRecursionWarning(ValidationWarning):
    pass

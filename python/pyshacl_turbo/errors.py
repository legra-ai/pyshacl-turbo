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


class ShapeLoadError(ReportableRuntimeError):
    def __init__(self, message, link):
        self.message = message
        self.link = link

    @property
    def args(self):
        return [self.message, self.link]

    def __str__(self):
        return f"{self.message}\nFor reference, see {self.link}"

    def __repr__(self):
        return f"ShapeLoadError: {self}"


class ConstraintLoadError(ReportableRuntimeError):
    def __init__(self, message, link):
        self.message = message
        self.link = link

    @property
    def args(self):
        return [self.message, self.link]

    def __str__(self):
        return f"{self.message}\nFor reference, see {self.link}"

    def __repr__(self):
        return f"ConstraintLoadError: {self}"


class ValidationWarning(RuntimeWarning):
    pass


class ShapeRecursionWarning(ValidationWarning):
    pass

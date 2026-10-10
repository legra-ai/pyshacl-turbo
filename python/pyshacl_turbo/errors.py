"""Warning categories exposed without a pySHACL runtime dependency."""


class ValidationWarning(RuntimeWarning):
    pass


class ShapeRecursionWarning(ValidationWarning):
    pass

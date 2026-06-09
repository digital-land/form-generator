def safe_quoted_string(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def tidy_string(s):
    """
    Ensure quotes are escaped; line returns are removed and double spaces are replaced with
    single spaces.
    """
    return safe_quoted_string(s).replace("\n", " ").replace("  ", " ")


def valid_class_name(ref):
    # TODO function for safe PEP8 class names
    class_name = ref.replace("-", " ").title().replace(" ", "")
    return class_name


def valid_field_name(s):
    # TODO function for safe PEP8 variable names
    field_name = s.replace("-", "_")
    return field_name


class SchemaValidationException(Exception):
    """
    Raised when data that doesn't conform with the schema is parsed.
    """

    def __init__(self, reasons):
        self.reasons = reasons
        super().__init__("; ".join(reasons))

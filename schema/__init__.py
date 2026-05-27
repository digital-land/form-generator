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


def valid_field_name(ref):
    # TODO function for safe PEP8 variable names
    field_name = ref.ref.replace("-", "_")
    return field_name

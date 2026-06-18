from pathlib import Path

from schema import safe_quoted_string

PROJECT_ROOT = Path(__file__).parent


def safe_literal(v):
    """
    Used in templating output Python code to build values to become python code.

    @return str
    """

    if isinstance(v, str):
        vs = safe_quoted_string(v)
        return f'"{vs}"'

    if v == None:
        return "None"

    if isinstance(v, (int, float)):
        return v

    raise ValueError(f"Can't build Python literal value for template for : {v}")

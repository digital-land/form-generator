import unittest

from schema import SchemaValidationException
from tests.sample_schema_nodes import Partnership, FaxNumber


class TestSchemaConditional(unittest.TestCase):
    """
    Conditional validation
    """

    def test_field_validation(self):
        """
        Email field is a test only sub-class of string
        """
        # happy path
        node = Partnership()
        node.load_payload({"person-a": {"email": "me@somewhere.co.uk"}})

        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload({"person-a": {"email": "me_at_somewhere.co.uk"}})

        self.assertIn("Email addresses must have an @", ctx.exception.reasons)

    def test_node_validation(self):
        """
        Validation check looks at a couple of places in the tree.
        """
        payload = {
            "person-a": {"email": "bob@somewhere.co.uk"},
            "person-b": {"email": "bob@somewhere.co.uk"},
        }
        node = Partnership()

        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertIn("Duplicate email addresses", ctx.exception.reasons)

    def test_boolean_field_requirement(self):
        """
        Boolean field determines if another field is required
        """
        payload = {"number": "0123", "is_international": False}

        node = FaxNumber()

        # valid
        node.load_payload(payload)

        # invalid
        payload["is_international"] = True
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertIn("International code needed", ctx.exception.reasons)

        # valid
        payload["international_code"] = "+44"
        node.load_payload(payload)

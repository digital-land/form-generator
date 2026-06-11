import unittest

from schema import SchemaValidationException
from schema.fields import (
    RepeatedField,
    SchemaNodeField,
    StringField,
)
from tests.sample_schema_nodes import ContactDetail, PhoneNumber, Partnership, FaxNumber


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


#
#
# Applies for application type
# `applies-if` + `application-type` + `value` or `in`
# Field is in scope only for one or more application types.
#
# Required when answer equals a value
# `required-if` + `field` + `value`
# Field is required when another field has a specific value.
#
# Required when answer is in a list
# `required-if` + `field` + `in`
# Field is required when another field is one of several values.
#
# Required when answer contains a value
# `required-if` + `field` + `contains`
# Field is required when a list or multi-value field contains a value.
#
# Required when value is empty
# `required-if` + `operator: empty`
# Field is required when another value has not been provided.
#
# Required when value is not empty
# `required-if` + `operator: not_empty`
# Field is required when another value has been provided.
#
# Required when any or all conditions match
# `any` / `all`
# Multi-condition rules must state whether one condition or every condition is needed.

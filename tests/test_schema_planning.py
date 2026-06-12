import unittest

from schema import SchemaValidationException
from schema.planning_application_specification import PreAppAdvice


class TestSchemaPlanning(unittest.TestCase):
    """
    These test use SchemaNodes from schema/planning_application_specification.py
    These are built from the spec. so these test could be brittle when/if upstream business logic
    changes.
    """

    def test_required_if_when_answer_true(self):
        """
        Required when answer equals a value
        `required-if` + `field` + `value`
        Field is required when another field has a specific value.
        """

        payload = {"advice-sought": True}

        expected = [
            "officer-name is needed when advice-sought is true",
            "reference is needed when advice-sought is true",
            "advice-date is needed when advice-sought is true",
            "advice-summary is needed when advice-sought is true",
        ]

        node = PreAppAdvice()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertEqual(expected, ctx.exception.reasons)

    @unittest.skip("TODO")
    def test_applies_if_application_type(self):
        """
        Applies for application type
        `applies-if` + `application-type` + `value` or `in`
        Field is in scope only for one or more application types.
        """
        pass

    @unittest.skip("TODO")
    def test_required_if_when_answer_in_list(self):
        """
        Required when answer is in a list
        `required-if` + `field` + `in`
        Field is required when another field is one of several values.
        """
        pass

    @unittest.skip("TODO")
    def test_required_if_when_answer_contains_value(self):
        """
        Required when answer contains a value
        `required-if` + `field` + `contains`
        Field is required when a list or multi-value field contains a value.
        """
        pass

    @unittest.skip("TODO")
    def test_required_if_when_value_is_empty(self):
        """
        Required when value is empty
        `required-if` + `operator: empty`
        Field is required when another value has not been provided.
        """
        pass

    @unittest.skip("TODO")
    def test_required_if_when_value_not_empty(self):
        """
        Required when value is not empty
        `required-if` + `operator: not_empty`
        Field is required when another value has been provided.
        """
        pass

    @unittest.skip("TODO")
    def test_required_when_any_all(self):
        """
        Required when any or all conditions match
        `any` / `all`
        Multi-condition rules must state whether one condition or every condition is needed.
        """
        pass

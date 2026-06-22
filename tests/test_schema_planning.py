import unittest

from schema import SchemaValidationException
from schema.planning_application import gla_planning_app_roots
from schema.planning_application_specification import (
    FloorspaceDetails,
    HoursOfOperation,
    InterestInLand,
    Lbc,
    PreAppAdvice,
    SiteInfo,
    SiteVisit,
)


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
            "officer-name is needed for current value in 'advice-sought'",
            "reference is needed for current value in 'advice-sought'",
            "advice-date is needed for current value in 'advice-sought'",
            "advice-summary is needed for current value in 'advice-sought'",
        ]

        node = PreAppAdvice()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertEqual(expected, ctx.exception.reasons)

    def test_gla_planning_app_roots_includes_full(self):
        """
        'full' application depends on the GLA specification profile so should be one of the
        GLA planning application roots.
        """
        refs = [root._ref for root in gla_planning_app_roots]
        self.assertIn("full", refs)

    def test_applies_if_application_type(self):
        """
        Applies for application type
        `applies-if` + `application-type` + `value` or `in`
        Field is in scope only for one or more application types.
        """
        payload = {
            "submission-details": {"application-types": ["lbc"]},
            "ownership_certs": {"lbc-owners": [{}]},
        }

        # listed building consent
        node = Lbc()

        # ownership_certs.lbc_owners is in scope when LBC application
        node.load_payload(payload)

        expected = "Field 'lbc-owners' out of scope in 'ownership-certs'"
        msg = "ownership_certs.lbc_owners not in scope for full applications"
        payload["submission-details"]["application-types"] = ["full"]
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertIn(expected, ctx.exception.reasons, msg)

    def test_required_if_when_answer_in_list(self):
        """
        Required when answer is in a list
        `required-if` + `field` + `in`
        Field is required when another field is one of several values.
        """
        payload = {"contact-type": "agent"}
        expected = ["contact-reference is needed for current value in 'contact-type'"]

        node = SiteVisit()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertEqual(expected, ctx.exception.reasons)

    def test_required_if_when_answer_contains_value(self):
        """
        Required when answer contains a value
        `required-if` + `field` + `contains`
        Field is required when a list or multi-value field contains a value.
        """

        payload = {"use": "sui"}
        expected = ["One or more matches required in field(s): use"]

        node = FloorspaceDetails()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertEqual(expected, ctx.exception.reasons)

    def test_required_if_when_value_is_empty(self):
        """
        Required when value is empty
        `required-if` + `operator: empty`
        Field is required when another value has not been provided.
        """

        operational_times_sample = {
            "schedule-days": ["monday"],
            "closed": False,
            "time-ranges": [
                {
                    "open-time": "5pm ish",
                    "close-time": "later than 6pm",
                }
            ],
        }

        payload = {"operational-times": [], "hours-not-known": False}
        expected = ["Field validation problem for: operational-times"]

        node = HoursOfOperation()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertEqual(expected, ctx.exception.reasons)

        msg = "Non-empty operational-times is valid"
        payload = {"operational-times": [operational_times_sample], "hours-not-known": False}
        node.load_payload(payload)
        self.assertIsNone(node.valid_node(), msg)

    def test_required_if_when_value_not_empty(self):
        """
        Required when value is not empty
        `required-if` + `operator: not_empty`
        Field is required when another value has been provided.
        """
        payload = {"known-constraints": ["conservation-area"]}
        expected = ["Field validation problem for: known-constraints"]

        node = SiteInfo()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertEqual(expected, ctx.exception.reasons)

    def test_required_when_any_all(self):
        """
        Required when any or all conditions match
        `any` / `all`
        Multi-condition rules must state whether one condition or every condition is needed.
        """
        payload = {
            "applicant-owns-land": False,
            "permission-obtained": False,
        }
        expected = "All fields need to match for field(s): applicant-owns-land, permission-obtained"

        node = InterestInLand()
        with self.assertRaises(SchemaValidationException) as ctx:
            node.load_payload(payload)

        self.assertIn(expected, ctx.exception.reasons)

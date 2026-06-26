import unittest

from schema.planning_application import schema_fusion
from schema.planning_application_ui import UserInterfaceOverride


class TestSchemaOverrides(unittest.TestCase):

    def test_happy_path(self):
        """
        Classes with the same name exist in both-

        schema/planning_application_specification.py
         and
        schema/planning_application_ui.py

        :func:`schema.planning_application.schema_fusion` should be pairing these up and dynamically
        adding a class built with multiple inheritance with both and adding this to the global
        symbols table.
        """
        from schema.planning_application import Person as FusionPerson
        from schema.planning_application_ui import Person as UiPerson
        from schema.planning_application_specification import Person as SpecificationPerson

        # expected vs. actual checks
        self.assertEqual("Person obj", SpecificationPerson._display)
        self.assertEqual("A Person", UiPerson._display)
        self.assertEqual("A Person", FusionPerson._display)

    def test_no_ui_class(self):
        """
        Specification classes not paired with a UI class should still be available from
        `schema.planning_application`.
        """

        # pre test check
        msg = (
            "This test assumes Agent doesn't have a UI override. Use any other "
            "planning_application_ui class instead."
        )
        with self.assertRaises(ImportError, msg=msg):
            from schema.planning_application_ui import Agent

        from schema.planning_application import Agent as FusionAgent

        self.assertEqual("Agent obj", FusionAgent._display)

    def test_schema_fields(self):

        from schema.planning_application import Agent as FusionAgent

        fields = FusionAgent.schema_fields()
        expected = {"company", "person", "reference", "user_role"}
        self.assertEqual(expected, set(fields))

    def test_schema_fusion(self):

        from schema.planning_application_ui import Person as UiPerson
        from schema.planning_application_specification import Person as SpecificationPerson

        sample_spec_nodes = [SpecificationPerson]
        sample_ui_nodes = [UiPerson]

        fusion_mapping = schema_fusion(sample_spec_nodes, sample_ui_nodes)
        msg = "Just expecting the Person specification to have a FusionCls"
        self.assertEqual({"Person"}, set(fusion_mapping.keys()), msg)

        class LonelyUi(UserInterfaceOverride):
            _display = "Please be my friend"

        msg = "Spare un-matched UI class"
        sample_ui_nodes.append(LonelyUi)
        with self.assertRaises(ValueError, msg=msg) as context:
            schema_fusion(sample_spec_nodes, sample_ui_nodes)

        self.assertIn("Un-matched UI classes", str(context.exception))

    def test_independent_fusion_classes(self):
        """
        Fusion classes are the specification classes optionally overridden with UI options.
        This is a regression test from when descendants of the source 'specification' classes
        were mutated by the process of building fusion classes.
        """
        from schema.planning_application_specification import AgentContact as SpecAgentContact
        from schema.planning_application_specification import ContactDetails as SpecContactDetails
        from schema.planning_application import AgentContact as FusionAgentContact
        from schema.planning_application import ContactDetails as FusionContactDetails

        spec_name = SpecAgentContact.contact_details.schema_node_cls.__name__
        self.assertEqual("ContactDetails", spec_name)

        fusion_name = FusionAgentContact.contact_details.schema_node_cls.__name__
        self.assertEqual("ContactDetails_FusionCls", fusion_name)

        msg = "Check for SchemaNode class inside Repeated field"

        spec_name = SpecContactDetails.phone_numbers.schema_field.schema_node_cls.__name__
        self.assertEqual("PhoneNumber", spec_name, msg)

        fusion_name = FusionContactDetails.phone_numbers.schema_field.schema_node_cls.__name__
        self.assertEqual("PhoneNumber_FusionCls", fusion_name, msg)

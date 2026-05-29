import unittest
from pathlib import Path

from builder.build_schema import segment_tree
from builder.planning_app_data_spec import (
    Application,
    Component,
    Field,
    Module,
    PlanningAppDataResolved,
    PlanningAppDataSpec,
)

DATA_PATH = Path(__file__).parent / "data"


class TestDataSpec(unittest.TestCase):
    def setUp(self):
        self.spec = PlanningAppDataSpec(planning_app_repo_path=DATA_PATH)
        self.resolved_spec = PlanningAppDataResolved(planning_app_repo_path=DATA_PATH)

    def test_spec_vs_resolved(self):
        """
        Acting on 'extends' keyword differentiates the resolved view from the literal view.
        """
        apps_literal = self.spec.applications
        apps_resolved = self.resolved_spec.applications

        expected_app_ref = "ldc-existing-use"
        self.assertIn(expected_app_ref, apps_literal)
        self.assertIn(expected_app_ref, apps_resolved)

        ldc_existing_literal = apps_literal[expected_app_ref]
        ldc_existing_resolved = apps_resolved[expected_app_ref]

        msg = (
            "Extends 'ldc' so should include 'site-details' module when resolved but not in "
            "literal spec."
        )
        expected_module = "site-details"
        self.assertNotIn(expected_module, [m["module"] for m in ldc_existing_literal.modules], msg)
        self.assertIn(expected_module, [m.ref for m in ldc_existing_resolved.modules], msg)

    def test_module_components(self):
        """
        @see doc. string in :class:`Module`. In summary, both components and fields are resolved
        for the module.
        """

        site_details_module = self.resolved_spec.modules["site-details"]

        msg = (
            "The 'site-details' module references the 'site-locations' field. This field "
            "references the 'site-location' component. It should only be in the components "
            "attribute."
        )

        field_entries = [f.ref for f in site_details_module.field_entries]
        self.assertIn("site-locations", field_entries, msg + " This is a component.")
        self.assertIn("reason", field_entries, msg + " This is a field.")

    def test_component_fields(self):

        site_location = self.resolved_spec.components["site-location"]
        field_refs = [f.ref for f in site_location.field_entries]
        self.assertIn("address-text", field_refs)

    def test_field_resolves_to_component(self):
        """
        When a module/application has a field that in turn refers to a component then the
        field in the module/application should retain the field's ref, not the module's ref.

        In modules["site-details"] the field is 'site-locations';
        In fields, site-locations.md:component: site-location
        """
        site_details_mod = self.resolved_spec.modules["site-details"]
        segment = segment_tree(schema_descriptor=site_details_mod)

        expected_field_name = "site-locations"
        descendant_refs = [s.ref for s in segment.descendants]
        self.assertIn(expected_field_name, descendant_refs)

    def test_component_descendant_of_component(self):
        """ """
        applicant = self.resolved_spec.components["applicant"]
        segment = segment_tree(schema_descriptor=applicant)

        msg = (
            "Test data has 'field: person' which should be a descendant and in turn it should have "
            "'field: first-name'"
        )

        expected_field_name = "person"
        descendant_refs = {s.ref: s for s in segment.descendants}
        self.assertIn(expected_field_name, descendant_refs, msg)

        grandchildren_field_refs = [s.ref for s in descendant_refs[expected_field_name].fields]
        self.assertIn("first-name", grandchildren_field_refs)

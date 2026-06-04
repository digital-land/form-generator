import unittest
from pathlib import Path

from builder.planning_app_data_spec import PlanningAppDataResolved, PlanningAppDataSpec

DATA_PATH = Path(__file__).parent / "data"


class TestDataSpec(unittest.TestCase):
    def planning_app_specs(self, dataset_label):
        """
        @param dataset_label: (str) - letter a, b etc.
        @return (PlanningAppDataSpec, PlanningAppDataResolved) for given test dataset.
        """
        spec = PlanningAppDataSpec(
            planning_app_repo_path=DATA_PATH,
            spec_files_path=f"specification_{dataset_label}",
        )
        resolved_spec = PlanningAppDataResolved(
            planning_app_repo_path=DATA_PATH,
            spec_files_path=f"specification_{dataset_label}",
        )
        return spec, resolved_spec

    def test_spec_vs_resolved(self):
        """
        Acting on 'extends' keyword differentiates the resolved view from the literal view.
        """
        spec_literal, spec_resolved = self.planning_app_specs("a")

        expected_app_ref = "ldc-existing-use"
        self.assertIn(expected_app_ref, spec_literal.applications)
        self.assertIn(expected_app_ref, spec_resolved.applications)

        ldc_existing_literal = spec_literal.applications[expected_app_ref]
        ldc_existing_resolved = spec_resolved.applications[expected_app_ref]

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
        _, spec_resolved = self.planning_app_specs("a")
        site_details_module = spec_resolved.modules["site-details"]

        msg = (
            "The 'site-details' module references the 'site-locations' field. This field "
            "references the 'site-location' component. It should only be in the components "
            "attribute."
        )

        field_entries = [f.origin.ref for f in site_details_module.field_entries]
        self.assertIn("site-locations", field_entries, msg + " This is a component.")
        self.assertIn("reason", field_entries, msg + " This is a field.")

    def test_component_fields(self):

        _, spec_resolved = self.planning_app_specs("a")
        site_location = spec_resolved.components["site-location"]
        field_refs = [f.origin.ref for f in site_location.field_entries]
        self.assertIn("address-text", field_refs)

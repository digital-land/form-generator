import unittest
from pathlib import Path

from builder import PROJECT_ROOT
from builder.build_schema import render_python, segment_tree
from builder.planning_app_data_spec import PlanningAppDataResolved


DATA_PATH = Path(__file__).parent / "data"


class TestBuildSchema(unittest.TestCase):

    def test_render_python(self):
        """
        Arbitrary choice of specification module to render as Python
        """

        specification = PlanningAppDataResolved(planning_app_repo_path=DATA_PATH)

        spec_segment = segment_tree(specification.modules["site-details"])

        py_out = render_python(
            project_root=PROJECT_ROOT,
            planning_application_spec_path=DATA_PATH,
            schema_items=[spec_segment],
        )

        expected_snippets = [
            ("class SiteLocations(SchemaNode):", "Descendant of SiteDetails"),
            ("class SiteDetails(SchemaNode):", "Parent node passed to render function"),
            ("site_locations = SchemaNodeField(", "SiteDetails field describing a descendant"),
            ("schema_node_cls=SiteLocations", "Link to child class"),
        ]
        for expected, msg in expected_snippets:
            self.assertIn(expected, py_out, msg)

import unittest
from pathlib import Path

from builder import PROJECT_ROOT
from builder.build_schema import render_python, walk_resolved_schema
from builder.planning_app_data_spec import PlanningAppDataResolved


DATA_PATH = Path(__file__).parent / "data"


class TestBuildSchema(unittest.TestCase):

    def test_render_python_a(self):
        """
        Arbitrary choice of specification module to render as Python
        """

        specification = PlanningAppDataResolved(
            planning_app_repo_path=DATA_PATH,
            spec_files_path="specification_a",
        )

        specification.spec_data = Path(DATA_PATH) / "specification_a" / "data"

        py_out = render_python(
            project_root=PROJECT_ROOT,
            planning_spec=specification,
        )

        expected_snippets = [
            ("class SiteLocation(SchemaNode):", "Descendant of SiteDetails"),
            ("class SiteDetails(SchemaNode):", "Parent node passed to render function"),
            (
                'site_locations = RepeatedField(schema_field=SchemaNodeField(ref="site-locations"',
                "SiteDetails field describing a descendant",
            ),
            ("schema_node_cls=SiteLocation", "Link to child class"),
            (
                'if self["contact-type"] in ["agent", "friend"] and not self["other-contact"]:',
                "Expected in GroundsLdc.valid_node",
            ),
            (
                'if self["first-name"].__len__() == 0 and not self["fullname"]:',
                "Expected in Person.valid_node - full name needed if first-name (str) is empty.",
            ),
        ]
        for expected, msg in expected_snippets:
            self.assertIn(expected, py_out, msg)

    def test_render_python_b(self):
        """
        Field should refer to Component but keep field details.

        Uses simplified test data to make this easier to follow.
        """

        specification = PlanningAppDataResolved(
            planning_app_repo_path=DATA_PATH,
            spec_files_path="specification_b",
        )
        specification.spec_data = Path(DATA_PATH) / "specification_a" / "data"

        py_out = render_python(
            project_root=PROJECT_ROOT,
            planning_spec=specification,
        )

        # just looking at one field in `class Menu(SchemaNode):`
        # wrong -
        # starter = SchemaNodeField(ref="starter", display="Dish", description="Dish details ",
        #                 schema_node_cls=Starter)
        expected_class = "class Dish(SchemaNode):"
        self.assertIn(expected_class, py_out)

        expected_snippet = (
            'starter = SchemaNodeField(ref="starter", display="Starter", '
            'description="Starter dish", schema_node_cls=Dish)'
        )
        self.assertIn(expected_snippet, py_out)

        msg = "Menu is a module so should render with module.ref as it's field name"
        expected_snippet = 'menu = SchemaNodeField(ref="menu"'
        self.assertIn(expected_snippet, py_out, msg)

        msg = "valid node rule: Reason should be given if dish doesn't contain cheese"
        expected_snippet = 'if self["contains-cheese"] == False and not self["reason"]:'
        self.assertIn(expected_snippet, py_out, msg)

    def test_reorder(self):

        specification = PlanningAppDataResolved(
            planning_app_repo_path=DATA_PATH,
            spec_files_path="specification_b",
        )
        spec_summary = set([(s.ref, s.__class__.__name__) for s in specification.schema_top_level])

        py_ordered = walk_resolved_schema(specification.schema_top_level)
        py_summary = set([(s.ref, s.__class__.__name__) for s in py_ordered])

        # not checking for correct order
        msg = "Should have same number of items in and out."
        self.assertEqual(spec_summary, py_summary, msg)

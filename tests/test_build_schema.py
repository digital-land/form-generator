import unittest
from pathlib import Path

from builder import PROJECT_ROOT
from builder.build_conditions import (
    BuildConditions,
    ContraintRule,
    RuleConjunction,
    RuleDisjunction,
)
from builder.build_schema import render_python, TemplatedBuilder, walk_resolved_schema
from builder.planning_app_data_spec import Field, PlanningAppDataResolved


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
                'site_locations = RepeatedField(required=True, schema_field=SchemaNodeField(ref="site-locations"',
                "SiteDetails field describing a descendant",
            ),
            ("schema_node_cls=SiteLocation", "Link to child class"),
            (
                'if (self["contact-type"] in ["agent", "friend"]) and (self.is_empty_field(\'other-contact\') == True):',
                "Expected in GroundsLdc.valid_node",
            ),
            (
                "if (self.is_empty_field('first-name') == True) and (self.is_empty_field('fullname') == True):",
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
        expected_snippet = (
            "if (self[\"contains-cheese\"] == False) and (self.is_empty_field('reason') == True):"
        )
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

    def test_render_validation_multiple_booleans(self):
        """
        Regression test for building `valid_node(..)` with 'OR' operator.
        """

        render = TemplatedBuilder(project_root=PROJECT_ROOT)

        example_field = Field(
            ref="contamination-assessment",
            name="",
            description="",
            content="",
            required_if=[
                {
                    "any": [
                        {"field": "is-contaminated-land", "value": True},
                        {"field": "is-suspected-contaminated-land", "value": True},
                        {"field": "proposed-use-contamination-risk", "value": True},
                    ]
                }
            ],
        )

        validation_simplified = BuildConditions().required_if_rules(example_field)

        template_context = {
            "class_name": "TestX",
            "validation_rules": validation_simplified,
        }
        py_output = render.build(template_context, "schema_tree_class.py.j2")

        expected_output = (
            'if ((self["is-contaminated-land"] == True) '
            'or (self["is-suspected-contaminated-land"] == True) '
            'or (self["proposed-use-contamination-risk"] == True)) '
            "and (self.is_empty_field('contamination-assessment') == True):"
        )

        self.assertIn(expected_output, py_output)

    def test_nested_operations_logic(self):
        """
        OR multiple conditions
        AND two of the OR groups.
        """
        rule = {}
        for label in ["a", "b", "c", "d", "e", "f"]:
            rule[label] = ContraintRule(switch_field=label, switch_value=True, operand="==")

        validation_simplified = [
            RuleConjunction(
                "rc0",
                RuleDisjunction("rc1", rule["a"], rule["b"], rule["c"]),
                RuleDisjunction("rc2", rule["d"], rule["e"], rule["f"]),
            )
        ]

        template_context = {
            "class_name": "TestX",
            "validation_rules": validation_simplified,
        }

        render = TemplatedBuilder(project_root=PROJECT_ROOT)
        py_output = render.build(template_context, "schema_tree_class.py.j2")

        expected_output = (
            'if ((self["a"] == True) or (self["b"] == True) or (self["c"] == True))'
            ' and ((self["d"] == True) or (self["e"] == True) or (self["f"] == True)):'
        )

        self.assertIn(expected_output, py_output)

    def test_render_contains_condition(self):
        """
        required_if's 'contains' clause when related to another field
        """
        """
        YML looks like this-

        - field: room-details
          required-if:
          - field: floorspace-details
            description: if floorspace-details contains an item where use is c1, c2, c2a or other
            contains:
              field: use
              in:
              - c1
              - c2
              - c2a
              - other
        """
        render = TemplatedBuilder(project_root=PROJECT_ROOT)

        example_field = Field(
            ref="room-details",
            name="Room details",
            content="",
            description="List of room changes for hotels, residential institutions and hostels",
            required_if=[
                {
                    "field": "floorspace-details",
                    "description": "if floorspace-details contains an item where use is c1, c2, c2a or other",
                    "contains": {
                        "field": "use",
                        "in": ["c1", "c2", "c2a", "other"],
                    },
                }
            ],
        )

        validation_simplified = BuildConditions().required_if_rules(example_field)

        template_context = {
            "class_name": "TestX",
            "validation_rules": validation_simplified,
        }
        py_output = render.build(template_context, "schema_tree_class.py.j2")

        expected_lines = [
            (
                'if (self["floorspace-details"] in ["c1", "c2", "c2a", "other"]) '
                "and (self.is_empty_field('room-details') == True):"
            ),
            (
                '{self.node_path}.room-details requires value from ["c1", "c2", "c2a", "other"]'
                " in {self.node_path}.floorspace-details"
            ),
        ]

        for expected in expected_lines:
            self.assertIn(expected, py_output)

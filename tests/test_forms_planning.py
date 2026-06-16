from schema.planning_application_specification import Employment
from tests.base import WebTestCase
from web_viewer.forms import schema_auto_form, FormTree


class TestFormsPlanning(WebTestCase):
    """
    Tests specific to planning applications data.
    When these break it could be a schema change so external and could be out of scope.
    """

    def test_multiple_use_component(self):
        """
        Employment has two fields (`existing_employees` and `proposed_employees`) both pointing at
        `Employees`. Prefixes must use field specific ref.
        """
        prefix = "test"
        node = Employment
        form = schema_auto_form(node)(prefix=prefix)

        results = [form]
        for descendant_node_field in node.descendant_schema_nodes():
            child_prefix = f"{prefix}.{descendant_node_field.ref}"

            descendant = descendant_node_field.schema_node_cls
            child_form = schema_auto_form(descendant)(prefix=child_prefix)
            results.append(child_form)

        # suffix is a WTForms addition
        actual_prefixes = set([f._prefix.removesuffix("-") for f in results])
        expected_prefixes = {"test", "test.existing-employees", "test.proposed-employees"}
        self.assertEqual(expected_prefixes, actual_prefixes)

    def test_usage_enum_field(self):
        """
        An enum that changes available options depending on values in schema tree.
        """

        def extract_html(form):
            rendered_field = ""
            for field in form:
                # target for test
                if field.name == "synthetic":
                    rendered_field += str(field.__html__())
            return rendered_field

        from schema.fields import EnumField, DynamicEnumField, EnumOption, SelectFilter
        from schema.node import SchemaNode

        class ExamplePlanningNode(SchemaNode):
            _ref = "unittest-example"

            specification_profile = EnumField(
                ref="specification-profile",
                display="Specification profile",
                select_options=[
                    EnumOption(key="core", label="MHCLG", description=""),
                    EnumOption(key="gla", label="GLA", description=""),
                ],
            )

            synthetic = DynamicEnumField(
                ref="synthetic",
                display="Synthetic",
                select_options=[
                    EnumOption(key="a", label="A", description=""),
                    EnumOption(key="b", label="B", description=""),
                    EnumOption(key="c", label="C", description=""),
                ],
                select_filter=[
                    SelectFilter(
                        node="specification-profile",
                        select_values=["core"],
                        key_values=["a", "b"],
                    ),
                    SelectFilter(
                        node="specification-profile",
                        select_values=["gla"],
                        key_values=["b", "c"],
                    ),
                ],
            )

        # example schema node
        form_tree = FormTree(root_node=ExamplePlanningNode)

        all_forms = form_tree.collection()
        self.assertEqual(1, len(all_forms), "Expecting nothing else in the tree")
        form = all_forms[0]

        actual = extract_html(form)
        expected = '<ul id="synthetic"></ul>'
        msg = "Node should be empty as there isn't a known value"
        self.assertEqual(expected, actual, msg)

        # Add value into node
        form_tree.load({"specification-profile": "core"})
        form = form_tree.collection()[0]

        actual = extract_html(form)
        expected = '<input id="contact_pref-0" name="contact_pref" type="radio" value="email">'
        msg = "Just A and B when 'core' is selected"
        self.assertIn('value="a"', actual, msg)
        self.assertIn('value="b"', actual, msg)
        self.assertNotIn('value="c"', actual, msg)

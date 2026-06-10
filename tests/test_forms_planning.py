from schema.planning_application import fusion_cls_map
from schema.planning_application_specification import Employment
from tests.base import WebTestCase
from web_viewer.forms import schema_auto_form


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

            # fusion nodes = user interface + specification
            descendant = descendant_node_field.schema_node_cls
            fusion_descendant = fusion_cls_map[descendant.__name__]

            child_form = schema_auto_form(fusion_descendant)(prefix=child_prefix)
            results.append(child_form)

        # suffix is a WTForms addition
        actual_prefixes = set([f._prefix.removesuffix("-") for f in results])
        expected_prefixes = {"test", "test.existing-employees", "test.proposed-employees"}
        self.assertEqual(expected_prefixes, actual_prefixes)

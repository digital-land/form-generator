from flask import render_template_string

from schema.planning_application import schema_fusion
from tests.base import WebTestCase
from tests.sample_schema_nodes import ContactDetail, FaxNumber, Partnership, PhoneNumber
from web_viewer.forms import schema_auto_form, FormTree


class TestForms(WebTestCase):

    def test_repeated_node_field_is_skipped_without_error(self):
        # `phones` is a RepeatedField wrapping a node - it describes descendants, so it
        # shouldn't become a form field and shouldn't raise
        form = schema_auto_form(ContactDetail)()

        self.assertNotIn("phones", form._fields)

    def test_node_field_is_skipped(self):
        # `fax` is a node field, rendered separately as its own card
        form = schema_auto_form(ContactDetail)()

        self.assertNotIn("fax", form._fields)

    def test_non_repeated_field_has_no_marker(self):
        # `email` is a plain string field - no '+' control
        form = schema_auto_form(ContactDetail)()

        self.assertIn("email", form._fields)
        self.assertIsNone(form.email.render_kw)

    def test_load_value(self):
        """ """

        # No UI overrides
        spec_classes = [ContactDetail, FaxNumber, Partnership, PhoneNumber]
        fusion_cls_map = schema_fusion(spec_classes, [])
        fusion_contact_details_cls = fusion_cls_map["Partnership"]

        form_tree = FormTree(root_node=fusion_contact_details_cls, fusion_cls_map=fusion_cls_map)

        # this should be in the same format as :meth:`FormTree.as_native`
        forced_value = {"person-a": {"fax-number": {"number": "123456789"}}}
        form_tree.load(forced_value)

        forms = form_tree.collection()

        template = (
            '{% from "main/macros.html" import render_form_card %}'
            "{% for form in forms %}{{ render_form_card(form) }}{% endfor %}"
        )

        html = render_template_string(
            template,
            forms=forms,
        )

        expected = (
            '<input class="form-control" id="person-a.fax-number-number" '
            'name="person-a.fax-number-number" type="text" value="123456789">'
        )
        self.assertIn(expected, html)

    def test_prefix_load(self):
        payload = {"person-a": {"email": "a@me.com", "fax-number": {"number": "123456789"}}}

        expected = {
            "person-a-": [("email", "a@me.com")],
            "person-a.fax-number-": [("number", "123456789")],
        }
        ftree = FormTree(root_node=None, fusion_cls_map=None)
        ftree.load(payload)

        # note - order doesn't actually matter.
        self.assertEqual(expected, ftree.loaded_values)

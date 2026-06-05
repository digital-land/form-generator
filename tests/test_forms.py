from tests.base import WebTestCase
from tests.sample_schema_nodes import ContactDetail
from web_viewer.forms import schema_auto_form


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

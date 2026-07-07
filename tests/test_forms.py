from flask import render_template_string

from tests.base import WebTestCase
from tests.sample_schema_nodes import Animal, ContactDetail, Partnership
from web_viewer.forms import FormFabricate, FormTree


class TestForms(WebTestCase):

    def render_forms(self, forms):
        """
        Helper to render html for `forms`
        """
        template = (
            '{% from "main/macros.html" import render_form_card %}'
            "{% for form in forms %}{{ render_form_card(form) }}{% endfor %}"
        )
        html = render_template_string(
            template,
            forms=forms,
        )
        return html

    def test_repeated_node_field_is_a_field_list(self):
        """
        `phones` is a RepeatedField wrapping a node - each entry is a subform holding the
        node's fields.

        These should end up as WTForms FieldList and FormFields.
        """
        form = FormFabricate.schema_auto_form(ContactDetail)()

        self.assertEqual("FieldList", form.phones.type)
        self.assertEqual("FormField", form.phones.entries[0].type)
        self.assertIn("number", form.phones.entries[0].form._fields)

    def test_load_value(self):
        """
        Data values appear in the form.
        """
        form_tree = FormTree(root_node=Partnership)

        # this should be in the same format as :meth:`FormTree.as_native`
        forced_value = {"person-a": {"fax-number": {"number": "123456789"}}}
        form_tree.load(forced_value)

        forms = form_tree.collection()

        html = self.render_forms(forms)
        expected = (
            '<input class="form-control" id="person-a.fax-number-number" '
            'name="person-a.fax-number-number" type="text" value="123456789">'
        )

        self.assertIn(expected, html)

    def test_load_repeated_node(self):
        """
        A payload with multiple entries for a repeated node renders one entry per item.
        """
        form_tree = FormTree(root_node=ContactDetail)
        form_tree.load({"phones": [{"number": "111"}, {"number": "222"}]})

        html = self.render_forms(form_tree.collection())

        for expected in [
            'name="phones-0-number"',
            'value="111"',
            'name="phones-1-number"',
            'value="222"',
        ]:
            self.assertIn(expected, html)

    def test_load_repeated_values(self):
        """
        A payload with multiple values for a repeated field renders one input per value.
        """
        form_tree = FormTree(root_node=Animal)
        form_tree.load({"keeper": {"email": "tim@thezoo.com"}, "location": ["zoo", "safari"]})

        html = self.render_forms(form_tree.collection())

        for expected in [
            'name="where-0"',
            'value="zoo"',
            'name="where-1"',
            'value="safari"',
        ]:
            self.assertIn(expected, html)

    def test_post_repeated_values(self):
        """
        Each entry the user added in the browser arrives in the POST under an indexed name
        and each item is accessible in the payload.
        """
        post_data = {"where-0": "zoo", "where-1": "safari", "animal_name": "Gila Monster"}
        with self.app.test_request_context("/", method="POST", data=post_data):
            form_tree = FormTree(root_node=Animal)
            payload = form_tree.as_native()

        self.assertEqual(["zoo", "safari"], payload["where"])

    def test_post_repeated_node(self):
        """
        Repeated node entries arrive as a list of dicts, one per entry.
        """
        post_data = {
            "email": "me@somewhere.com",
            "phones-0-number": "111",
            "phones-1-number": "222",
        }
        with self.app.test_request_context("/", method="POST", data=post_data):
            form_tree = FormTree(root_node=ContactDetail)
            payload = form_tree.as_native()

        self.assertEqual([{"number": "111"}, {"number": "222"}], payload["phones"])

    def test_post_blank_repeated_entries_dropped(self):
        """
        The always-rendered blank entry (and any entry left blank) carries no information
        so shouldn't create an item in the payload.
        """
        post_data = {"email": "me@somewhere.com", "phones-0-number": ""}
        with self.app.test_request_context("/", method="POST", data=post_data):
            form_tree = FormTree(root_node=ContactDetail)
            payload = form_tree.as_native()

        self.assertEqual([], payload["phones"])

    def test_enum_filter(self):
        """
        An enum can look into the schema node tree for a value which determines which
        enum options should be available.
        """

        def extract_html(all_forms):
            rendered_field = ""
            for form in all_forms:
                for field in form:
                    # target for test
                    if field.name == "contact_pref":
                        rendered_field += str(field.__html__())
            return rendered_field

        # example schema node
        form_tree = FormTree(root_node=ContactDetail)

        all_forms = form_tree.collection()
        actual = extract_html(all_forms)
        expected = '<ul id="contact_pref"></ul>'
        msg = "Node doesn't contain email,fax or phone so no prefernce options are available"
        self.assertEqual(expected, actual, msg)

        # Add value into node
        form_tree.load({"email": "me@somewhere.co.uk"})
        all_forms = form_tree.collection()
        actual = extract_html(all_forms)
        expected = '<input id="contact_pref-0" name="contact_pref" type="radio" value="email">'
        msg = "Node has email address so this should be in preferences enum field"
        self.assertIn(expected, actual, msg)

    def test_repeated_values(self):
        """
        RepeatedField of a StringField renders button in HTML.
        """
        form_tree = FormTree(root_node=Animal)
        forms = form_tree.collection()

        html = self.render_forms(forms)
        expected = 'title="Add another" onclick='
        self.assertIn(expected, html)

    def test_out_of_scope_leaf_field_hidden(self):
        """
        A leaf field a node puts out of scope isn't rendered.
        """
        # Animal puts `location` (the `where` repeated field) out of scope for Bob
        form_tree = FormTree(root_node=Animal)
        form_tree.load({"keeper": {"email": "bob@thezoo.com"}})
        html = self.render_forms(form_tree.collection())
        self.assertNotIn('name="where-0"', html)

        # in scope for anyone else
        form_tree = FormTree(root_node=Animal)
        form_tree.load({"keeper": {"email": "tim@thezoo.com"}})
        html = self.render_forms(form_tree.collection())
        self.assertIn('name="where-0"', html)

    def test_out_of_scope_node_card_hidden(self):
        """
        A whole child node (and its descendant cards) a node puts out of scope isn't rendered.
        """
        # Partnership puts the `person-b` node out of scope for a sole trader
        form_tree = FormTree(root_node=Partnership)
        form_tree.load({"person-a": {"email": "sole-trader@me.com"}})
        html = self.render_forms(form_tree.collection())
        self.assertNotIn("person-b", html)
        self.assertIn("person-a", html)

        # both people in scope otherwise
        form_tree = FormTree(root_node=Partnership)
        form_tree.load({"person-a": {"email": "a@me.com"}})
        html = self.render_forms(form_tree.collection())
        self.assertIn("person-b", html)

    def test_dynamic_enums(self):
        """
        Dynamic enums must have access to loaded data
        """
        bob_expected = "reptilia"
        bob_payload = {"keeper": {"email": "bob@thezoo.com"}, "animal-name": "Gila Monster"}

        tim_expected = "mammalia"
        tim_payload = {"keeper": {"email": "tim@thezoo.com"}, "animal-name": "Doormouse"}

        form_tree = FormTree(root_node=Animal)
        form_tree.load(bob_payload)
        forms = form_tree.collection()
        html = self.render_forms(forms)

        self.assertIn(bob_expected, html)
        self.assertNotIn(tim_expected, html)

        form_tree = FormTree(root_node=Animal)
        form_tree.load(tim_payload)
        forms = form_tree.collection()
        html = self.render_forms(forms)

        self.assertNotIn(bob_expected, html)
        self.assertIn(tim_expected, html)

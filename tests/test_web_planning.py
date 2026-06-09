from tests.base import WebTestCase

from web_viewer.forms import schema_auto_form


class TestWebPlanning(WebTestCase):
    """
    Web pages using schema.planning_application
    """

    def test_application_root(self):
        response = self.client.get("/application/outline-all")
        self.assertEqual(response.status_code, 200)

        for expected, msg in [
            ("Outline Planning Permission with All Matters Reserved", "Page title"),
            ("Agent contact details", "Sub form"),
            (
                '<h5 class="mb-0">A Person</h5>',
                "planning_application_ui should substitute 'Person obj' for 'A Person'",
            ),
        ]:
            self.assertIn(expected, response.text, msg)

    def test_schema_overrides_simple_form(self):

        from schema.planning_application import Person as FusionPerson

        form = schema_auto_form(FusionPerson)()

        msg = "In _specification it's 'Person obj' , in _ui it's 'A Person'"
        self.assertEqual("A Person", form._display, msg)

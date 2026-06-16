from flask import render_template_string

from schema.planning_application import SubmissionDetails
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

    def test_application_post_returns_json_document(self):
        response = self.client.post("/application/outline-all", data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("application/json", response.mimetype)

        # data not checked
        self.assertTrue(response.is_json)

    def test_submission_details(self):
        """
        The specification allows many application types in a single payload. For demo web viewer
        simplify to one so don't show the big enum just set application's reference when in web
        view.
        """
        form = schema_auto_form(SubmissionDetails)()

        html = render_template_string(
            '{% from "main/macros.html" import render_form_card %}{{ render_form_card(form) }}',
            form=form,
        )

        self.assertNotIn("District Council", html)

import html
import json
import re
from pathlib import Path

from flask import render_template_string

from schema.planning_application import SubmissionDetails
from tests.base import WebTestCase
from web_viewer.forms import schema_auto_form
import unittest

DATA_PATH = Path(__file__).parent / "data"


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

    def test_application_pdf(self):
        response = self.client.get("/application/full/pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual("application/pdf", response.mimetype)
        self.assertGreater(len(response.data), 1000)

    def test_application_post_returns_payload_page(self):
        response = self.client.post("/application/outline-all", data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("text/html", response.mimetype)

        for expected, msg in [
            ("View payload", "Page heading"),
            ("<textarea", "Payload text area"),
            ("Validation", "Validation results area"),
        ]:
            self.assertIn(expected, response.text, msg)

    def text_area_payload(self, response_text):
        """
        The page returned when submitting an application contains a textarea holding
        JSON payload. Find this, de-serialise from JSON.

        @return: mixed native python values
        """
        match = re.search(r"<textarea[^>]*>(.*?)</textarea>", response_text, re.DOTALL)
        self.assertIsNotNone(match, "Payload textarea not found")

        # textarea contents are HTML-escaped (e.g. &#34;) so unescape before parsing
        payload = json.loads(html.unescape(match.group(1)))
        return payload

    def test_agent_reference_round_trips_into_payload(self):
        """
        POST an 'Agent reference' value, extract the JSON shown in the payload textarea
        and confirm the value survived the round trip through the schema.
        """
        web_forms = {"agent-contact-agent_reference": "AGENT-XYZ-123", "email": "me@somewhere.com"}
        response = self.client.post(
            "/application/outline-all",
            data=web_forms,
        )
        self.assertEqual(response.status_code, 200)

        payload = self.text_area_payload(response.text)
        self.assertEqual(
            "AGENT-XYZ-123",
            payload["agent-contact"]["agent-reference"],
        )

    def test_evaluate_full_application_is_valid(self):
        """
        POST the full application payload to the evaluate view and confirm it reports valid.
        """
        payload = (DATA_PATH / "web_payloads" / "application_full.json").read_text()

        response = self.client.post("/evaluate", data={"payload": payload})

        self.assertEqual(response.status_code, 200)
        self.assertIn("The payload is valid.", response.text)

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

    def test_local_variance(self):

        gla_only_known_value = 'type="radio" value="student-accommodation"'

        response = self.client.get("/application/outline-all?profile=mhclg-core")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(gla_only_known_value, response.text)

        response = self.client.get("/application/outline-all?profile=gla")
        self.assertEqual(response.status_code, 200)
        self.assertIn(gla_only_known_value, response.text)

    def test_prune_empty_values(self):
        """
        Empty string and None are both treated as empty values. These fields aren't needed in the
        returned payload.
        """

        web_forms = {
            "agent-contact-agent_reference": "",
            "agent-contact.contact-details-email": "me@somewhere.com",
        }

        response = self.client.post("/application/outline-all", data=web_forms)
        self.assertEqual(response.status_code, 200)
        payload = self.text_area_payload(response.text)

        self.assertIn("agent-contact", payload, "Other fields in this section are required")

        msg = (
            "Reference not supplied so field shouldn't be present but email is so contact details "
            "node not empty so should be there."
        )
        self.assertNotIn("agent-reference", payload["agent-contact"], msg)

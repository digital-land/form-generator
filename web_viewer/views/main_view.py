import json

from flask import Blueprint, Response, render_template, request

from schema.planning_application import planning_application_roots_mapping
from web_viewer.forms import FormTree

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/", methods=["GET"])
def index():
    page_vars = {"application_types": planning_application_roots_mapping}
    return render_template("main/index.html", **page_vars)


@main_blueprint.route("/application/<application_ref>", methods=["GET", "POST"])
def application(application_ref):

    root_schema_class = planning_application_roots_mapping[application_ref]

    form_tree = FormTree(root_node=root_schema_class)

    # Set the planning application type. The options around this are hidden in the web forms
    # because this demo app lists them on the front page and builds forms based on that initial
    # decision. It's a list because the specification support multiple application types within
    # a single payload.
    empty_app_fixture = {
        "submission-details": {
            "application_types": [application_ref],
            "specification-profile": "gla",  # "mhclg-core",
        },
        "agent-contact": {"agent-reference": "hello agent"},  # test
    }

    form_tree.load(empty_app_fixture)

    forms = form_tree.collection()

    if request.method == "POST":

        # build dictionaries in schema layout. Empty strings, no Nones and no concept
        # of required or optional fields. That's done by the schema.
        payload = form_tree.as_native()

        # node = root_schema_class()
        # try:
        #     node.load_payload(payload)
        # except SchemaValidationException as e:
        #     return Response(
        #         json.dumps({"errors": e.reasons}, indent=2, ensure_ascii=False),
        #         status=400,
        #         mimetype="application/json",
        #     )
        #
        # document = node_to_document(node)
        return Response(
            json.dumps(payload, indent=2, ensure_ascii=False),
            mimetype="application/json",
        )

    return render_template("main/application.html", application_ref=application_ref, forms=forms)

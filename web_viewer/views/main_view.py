import json
from io import BytesIO

from flask import Blueprint, render_template, request, send_file

from schema import SchemaValidationException
from pdf_builder.generate_application import GenerateApplication
from schema.planning_application import (
    fusion_cls_map,
    planning_application_roots,
    planning_application_roots_mapping,
    gla_planning_app_roots,
)
from schema.planning_application_specification import SubmissionDetails
from web_viewer.forms import FormTree

main_blueprint = Blueprint("main", __name__)

# specification profiles supported by the schema
SPECIFICATION_PROFILES = {o.key for o in SubmissionDetails.specification_profile.select_options}


def _validated_profile():
    """
    @return: (str) specification profile
    """
    profile = request.args.get("profile", "mhclg-core")
    assert profile in SPECIFICATION_PROFILES
    return profile


@main_blueprint.route("/", methods=["GET"])
def index():

    application_types = sorted(
        planning_application_roots,
        key=lambda node_class: (node_class._display or node_class._ref).lower(),
    )

    # gla_planning_app_roots - are root nodes (aka applications) which need to know if the value
    # in submission-details.specification-profile == 'gla'
    page_vars = {
        "application_types": application_types,
        "gla_planning_app_roots": gla_planning_app_roots,
    }
    return render_template("main/index.html", **page_vars)


@main_blueprint.route("/application/<application_ref>", methods=["GET", "POST"])
def application(application_ref):

    root_schema_class = planning_application_roots_mapping[application_ref]
    profile = _validated_profile()

    form_tree = FormTree(root_node=root_schema_class)

    # Set the planning application type. The options around this are hidden in the web forms
    # because this demo app lists them on the front page and builds forms based on that initial
    # decision. It's a list because the specification support multiple application types within
    # a single payload.
    empty_app_fixture = {
        "submission-details": {
            "application-types": [application_ref],
            "specification-profile": profile,
        },
    }

    form_tree.load(empty_app_fixture)

    forms = form_tree.collection()

    if request.method == "POST":

        # build dictionaries in schema layout. Empty strings, no Nones and no concept
        # of required or optional fields. That's done by the schema.
        form_payload = form_tree.as_native()

        # load the form data into the schema and validate it; reasons is empty when valid
        reasons = []
        node = root_schema_class()
        try:
            node.load_payload(form_payload)
        except SchemaValidationException as e:
            reasons = e.reasons

        # the displayed payload comes from the schema node, not the raw form data
        payload = json.dumps(node.as_native(), indent=2, ensure_ascii=False)

        return render_template(
            "main/view_payload.html",
            application_ref=application_ref,
            payload=payload,
            reasons=reasons,
        )

    return render_template("main/application.html", application_ref=application_ref, forms=forms)


@main_blueprint.route("/application/<application_ref>/pdf", methods=["GET"])
def application_pdf(application_ref):

    # validate the ref is a known application type before generating anything
    planning_application_roots_mapping[application_ref]
    profile = _validated_profile()

    buffer = BytesIO()
    generator = GenerateApplication(
        output_filepath=buffer,
        application_ref=application_ref,
        schema_node_map=fusion_cls_map,
    )
    generator.set_specification_profile(profile)
    generator.go()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"{application_ref}-{profile}.pdf",
    )

from io import BytesIO
import json
from pathlib import Path

from flask import Blueprint, abort, current_app, render_template, request, send_file

from pdf_builder.generate_application import GenerateApplication
from schema import SchemaValidationException
from schema.parser import SchemaTreeParser
from schema.planning_application import (
    fusion_cls_map,
    planning_application_roots,
    planning_application_roots_mapping,
    gla_planning_app_roots,
)
from schema.planning_application_specification import SubmissionDetails
from web_viewer.forms import FormTree

# Example payloads from unittest data
TEST_DATA_PATH = Path(__file__).parent.parent.parent / "tests" / "data" / "web_payloads"
assert TEST_DATA_PATH.is_dir(), "Example payloads in unittest data not found"

main_blueprint = Blueprint("main", __name__)

# specification profiles supported by the schema, mapping key to display label
SPECIFICATION_PROFILES = {
    o.key: o.label for o in SubmissionDetails.specification_profile.select_options
}

DEMO_SPECIFICATION_PROFILES = {}
for k, v in SPECIFICATION_PROFILES.items():
    if k == "gla":
        DEMO_SPECIFICATION_PROFILES[k] = "Greater London Authority (GLA)"
    else:
        DEMO_SPECIFICATION_PROFILES[k] = v

DEMO_SPECIFICATION_PROFILES["gmca"] = "Greater Manchester (GMCA)"


def _validated_profile():
    """
    @return: (str) specification profile
    """
    profile = request.args.get("profile", "mhclg-core")
    if profile not in SPECIFICATION_PROFILES:
        abort(
            404, description="Sorry, that option isn't actually available, it's just a placeholder"
        )
    return profile


@main_blueprint.route("/", methods=["GET"])
def index():

    return render_template("landing_page.html")


@main_blueprint.route("/application", methods=["GET"])
def application_index():

    application_types = sorted(
        planning_application_roots,
        key=lambda node_class: (node_class._display or node_class._ref).lower(),
    )

    # gla_planning_app_roots - are root nodes (aka applications) which need to know if the value
    # in submission-details.specification-profile == 'gla'
    page_vars = {
        "application_types": application_types,
        "gla_planning_app_roots": gla_planning_app_roots,
        "specification_profiles": DEMO_SPECIFICATION_PROFILES,
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
        schema_payload = node.as_native()
        payload = json.dumps(schema_payload, indent=2, ensure_ascii=False)

        return render_template(
            "main/view_payload.html",
            application_ref=application_ref,
            payload=payload,
            reasons=reasons,
        )

    forms = form_tree.collection()
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


@main_blueprint.route("/evaluate", methods=["GET", "POST"])
def evaluate_payload():
    """
    Render the application page so a user can supply their own JSON document to be
    evaluated. No form tree or profile as these are determined from the payload.
    POSTs to :func:`application`, which performs the evaluation.
    """
    page_vars = {"nav_menu_active": "evaluate_payload"}

    if request.method == "POST":
        if request.mimetype != "application/x-www-form-urlencoded":
            abort(415, description="Payload must be submitted as form data")

        # the textarea value is the serialised JSON the user pasted; pass it to load_json
        # unparsed and let the parser deserialise and validate it
        serialised_payload = request.form.get("payload", "")
        # checkbox: only present in the form data when ticked
        simplify = request.form.get("simplify") is not None
        parser = SchemaTreeParser(schema_node_cls=None)
        reasons = []
        node = None
        try:
            node = parser.load_json(
                serialised_payload,
                application_type_map=planning_application_roots_mapping,
            )

        except SchemaValidationException as e:
            reasons = e.reasons

        # default to echoing the user supplied payload. When the user opts to simplify and the
        # payload is valid, return the schema built version instead (as the application view does)
        payload = serialised_payload
        if simplify and not reasons and node is not None:
            payload = json.dumps(node.as_native(), indent=2, ensure_ascii=False)

        page_vars.update({"payload": payload, "reasons": reasons, "simplify": simplify})

    return render_template("main/view_payload.html", **page_vars)


@main_blueprint.route("/example_payload")
@main_blueprint.route("/example_payload/<example_ref>/<view_format>")
def example_payload(example_ref=None, view_format=None):
    """
    Use example JSON payloads in web forms and the evaluate interface.

    Examples are taken from local unittest data and the PLANNING_APPLICATION_DATA_SPECIFICATION_REPO
    if set in the config.
    """

    planning_spec_repo_path = current_app.config.get("PLANNING_APPLICATION_DATA_SPECIFICATION_REPO")
    page_vars = {
        "nav_menu_active": "example_payload",
        "planning_app_spec_repo_available": planning_spec_repo_path is not None,
    }

    # permitted examples are hardcoded. This should be moved when it gets big. External
    # files carry a security risk so just repo-local files for now.
    # example_ref (str) -> details (dict)
    #                         'path' : filesystem location of JSON file
    #                         'title' : (str)
    #                         'description': (str)
    examples = {
        "test_full": {
            "path": TEST_DATA_PATH / "application_full.json",
            "title": "Full Application",
            "description": "Example full planning application taken from unittest data.",
        }
    }

    # When PLANNING_APPLICATION_DATA_SPECIFICATION_REPO is available use all example application
    # types as examples.
    if planning_spec_repo_path:
        spec_example_path = (
            Path(planning_spec_repo_path) / "specification" / "example" / "application-type"
        )

        for spec_example_file in spec_example_path.glob("*.json"):
            # upstream repo for url safe names - urlencode if not
            examples[spec_example_file.stem] = {
                "path": spec_example_file,
                "title": spec_example_file.stem,
                "description": (
                    "Example taken from https://github.com/digital-land/"
                    "planning-application-data-specification"
                ),
            }

    # Listing of available examples
    if example_ref is None or view_format is None:
        return render_template("main/example_payloads.html", **page_vars, examples=examples)

    if example_ref not in examples:
        abort(404, description="Unknown example")

    if not examples[example_ref]["path"].exists():
        abort(500, description="Example doesn't exist on filesystem")

    with open(examples[example_ref]["path"]) as f:
        example_payload_serialised = f.read()
        example_payload = json.loads(example_payload_serialised)

    sub_details = example_payload.get("submission-details")

    if not sub_details:
        abort(500, description="submission-details not found in example")

    spec_profile = sub_details.get("specification-profile")
    if spec_profile not in SPECIFICATION_PROFILES:
        abort(500, description="Unsupported specification-profile")

    application_types = sub_details.get("application-types")

    if len(application_types) != 1:
        abort(500, description="Only single application type per doc. is supported")

    application_ref = application_types[0]
    root_schema_class = planning_application_roots_mapping.get(application_ref)
    if root_schema_class is None:
        abort(500, description="Unsupported application type")

    if view_format == "web":

        form_tree = FormTree(root_node=root_schema_class)
        form_tree.load(example_payload)
        forms = form_tree.collection()
        return render_template(
            "main/application.html",
            application_ref=application_ref,
            forms=forms,
            **page_vars,
        )

    elif view_format == "evaluate":

        return render_template(
            "main/view_payload.html", **page_vars, payload=example_payload_serialised
        )

    else:
        abort(404, "Unknown view format")

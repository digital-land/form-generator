import json

from flask import Blueprint, Response, render_template, request

from schema.planning_application import fusion_cls_map, planning_application_roots_mapping
from web_viewer.forms import forms_extract, schema_auto_form

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/", methods=["GET"])
def index():
    page_vars = {"application_types": planning_application_roots_mapping}
    return render_template("main/index.html", **page_vars)


@main_blueprint.route("/application/<application_ref>", methods=["GET", "POST"])
def application(application_ref):

    def collect_forms(node, prefix=None):
        if prefix is None:
            prefix = ""

        form = schema_auto_form(node)(prefix=prefix)
        results = [form]

        for descendant_node_field in node.descendant_schema_nodes():

            if prefix:
                child_prefix = f"{prefix}.{descendant_node_field.ref}"
            else:
                child_prefix = descendant_node_field.ref

            # fusion nodes = user interface + specification
            descendant = descendant_node_field.schema_node_cls
            fusion_descendant = fusion_cls_map[descendant.__name__]

            results.extend(collect_forms(fusion_descendant, prefix=child_prefix))
        return results

    root_schema_class = planning_application_roots_mapping[application_ref]
    forms = collect_forms(root_schema_class)

    if request.method == "POST":

        # TODO - forms aren't being validated
        # e.g.
        # for form in forms:
        #     print(form._prefix, str(form), form.validate_on_submit())

        payload = forms_extract(forms)

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

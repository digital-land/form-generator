from flask import Blueprint, render_template

from schema.planning_applications import schema_node_root_mapping
from web_viewer.forms import schema_auto_form

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/", methods=["GET"])
def index():
    page_vars = {"application_types": schema_node_root_mapping}
    return render_template("main/index.html", **page_vars)


@main_blueprint.route("/application/<application_ref>", methods=["GET", "POST"])
def application(application_ref):

    def collect_forms(node, prefix=None):
        if prefix is None:
            prefix = ""

        form = schema_auto_form(node)(prefix=prefix)
        results = [form]
        for descendant in node.descendant_schema_nodes():
            child_prefix = f"{prefix}.{descendant._ref}" if prefix else descendant._ref
            results.extend(collect_forms(descendant, prefix=child_prefix))
        return results

    root_schema_class = schema_node_root_mapping[application_ref]
    forms = collect_forms(root_schema_class)

    return render_template("main/application.html", application_ref=application_ref, forms=forms)

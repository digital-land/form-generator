import csv
from functools import cached_property
import os
import warnings

from jinja2 import Environment, FileSystemLoader

from builder.planning_app_data_spec import (
    ComponentResolved,
    Field,
    ModuleResolved,
    PlanningAppDataResolved,
)
from schema import valid_class_name, valid_field_name, tidy_string
from schema.schema_tree import BooleanField, EnumField, EnumOption, SchemaSegment, StringField

SHOW_WARNINGS = False


class FormBuilder:
    """
    Render WTForm class from a template.
    """

    def __init__(self, project_root):

        self.templates_path = project_root / "form_templates"
        self.output_path = project_root / "web_viewer" / "forms"

    @cached_property
    def template_env(self):
        return Environment(loader=FileSystemLoader(self.templates_path))

    def build(self, context, template_name):
        """
        Build output python code.

        @param context: dict. with the following `key :  value`
            name : (str) - name of form

        @return: (str)
        """
        template = self.template_env.get_template(template_name)
        output = template.render(**context)
        return output


def segment_tree(schema_descriptor):
    """
    Build tree of SchemaSegment objects by collapsing upstream Module, Component and Field
    classes into a simpler tree.

    @param namespace: (str)
    @param schema_descriptor: (subclass of :class:`SchemaBase`)
    """

    # 'ref' must be unique in the space. e.g. 'Field', 'Component' etc.
    namespace = schema_descriptor.__class__.__name__

    # ApplicationResolved, ComponentResolved, Field, ModuleResolved

    s = SchemaSegment(
        ref=schema_descriptor.ref,
        namespace=namespace,
        name=schema_descriptor.name,
        description=schema_descriptor.description,
    )

    children = getattr(schema_descriptor, "field_entries", [])
    children.extend(getattr(schema_descriptor, "fields", []))
    children.extend(getattr(schema_descriptor, "modules", []))

    for child in children:
        if isinstance(child, Field):
            s.fields.append(child)
        elif isinstance(child, (ComponentResolved, ModuleResolved)):
            next_layer_fieldset = segment_tree(child)
            s.descendants.append(next_layer_fieldset)

        else:
            raise NotImplementedError(f"Unknown field_entries item: {child}")

    return s


def print_segment_tree(spec_segment, depth=0):
    print("\t" * depth + spec_segment.ref)
    for f in spec_segment.fields:
        print("\t" * (depth + 1) + f": {f.ref}")

    for d in spec_segment.descendants:
        print_segment_tree(d, depth=depth + 1)


def restructured_spec(spec_path):
    """

    @param spec_path: (str) - filesystem path for .md formatted specification
    @return (list) one item per planning application
    """

    specification = PlanningAppDataResolved(planning_app_repo_path=spec_path)

    apps = []
    for app_def in specification.applications.values():
        application_spec_segment = segment_tree(app_def)
        apps.append(application_spec_segment)

        # print(f"----{app_name}----")
        # print_segment_tree(application_spec_segment)

    return apps


def walk_schema_tree(spec_segment):
    """
    Recursively iterate a :class:`SchemaSegment` tree yielding each :class:`SchemaSegment`.
    """
    spec_segments = spec_segment if isinstance(spec_segment, list) else [spec_segment]
    for s in spec_segments:
        yield from walk_schema_tree(s.descendants)
        yield s


def render_python(project_root, planning_application_spec_path):
    """
    @param project_root: (str)
    @param planning_application_spec_path: (str) filesystem location of git repo
            https://github.com/digital-land/planning-application-data-specification/
    """

    form_builder = FormBuilder(project_root=project_root)
    py_output = form_builder.build(dict(document_header=True), "schema_tree_class.py.j2")

    spec_simplified = restructured_spec(planning_application_spec_path)

    # assumption - refs are primary keys
    segment_register = {}
    segment_class_map = {}  # class_name -> schema_segment
    for application_spec_segment in spec_simplified:

        for schema_segment in walk_schema_tree(application_spec_segment):
            # print(schema_segment.ref)

            if schema_segment.namespace not in segment_register:
                segment_register[schema_segment.namespace] = {}

            if schema_segment.ref in segment_register[schema_segment.namespace]:
                if schema_segment != segment_register[schema_segment.namespace][schema_segment.ref]:

                    # debug with- print_segment_tree(segment_register[schema_segment.ref])
                    msg = f"Expected ref to be primary key. Failed for {schema_segment.ref}"
                    raise ValueError(msg)

            else:
                segment_register[schema_segment.namespace][schema_segment.ref] = schema_segment

                fields_simplified = []
                for f in schema_segment.fields:

                    field_name = valid_field_name(f)
                    if field_name in ["_ref", "_display", "_description"]:
                        raise ValueError("Reserved word for schema classes found as field name.")

                    field_info = {
                        "display": f.name,
                        "description": f.description,
                    }

                    if f.datatype == "string":
                        schema_field = StringField(**field_info)
                    elif f.datatype == "boolean":
                        schema_field = BooleanField(**field_info)
                    elif f.datatype == "enum":

                        # there is a codelist .md file with field names, for now, I'm
                        # not using this.
                        csv_file = os.path.join(
                            planning_application_spec_path,
                            "data",
                            "codelist",
                            f"{f.codelist}.csv",
                        )

                        if not os.path.exists(csv_file):

                            # temp holding pattern
                            schema_field = StringField(**field_info)

                            if SHOW_WARNINGS:
                                warnings.warn(
                                    f"TODO missing file {csv_file} is probably an http source"
                                )

                        else:

                            select_options = []
                            with open(csv_file) as f:

                                csv_r = csv.DictReader(f)

                                if (
                                    "reference" not in csv_r.fieldnames
                                    or "name" not in csv_r.fieldnames
                                ):
                                    msg = "TODO: Field names should be mapped from field schema"
                                    raise NotImplementedError(msg)

                                for r in csv_r:
                                    e = EnumOption(
                                        key=r["reference"],
                                        label=r["name"],
                                        description=r.get("description", None),
                                    )
                                    select_options.append(e)

                            schema_field = EnumField(select_options=select_options, **field_info)

                    else:
                        # default used for now
                        schema_field = StringField(**field_info)
                        if SHOW_WARNINGS:
                            warnings.warn(f"Unknown field type {f.datatype}")

                    fields_simplified.append((field_name, schema_field))

                # does
                class_name = valid_class_name(schema_segment.ref)

                # just vanity - I don't want the namespace in the class name unless it does
                # overlap
                if class_name in segment_class_map:
                    class_name = valid_class_name(schema_segment.ref + schema_segment.namespace)

                segment_class_map[class_name] = schema_segment

                # Look up class name of the segments that are children of schema_segment
                # the name is needed by the template

                descendants_simplified = []
                for d_segment in schema_segment.descendants:

                    for k, v in segment_class_map.items():
                        if v == d_segment:

                            # TODO - SchemaNodeField should render itself with repr but class
                            # is out of scope here. For now, template emulates repr

                            node_info = {
                                "field_name": valid_field_name(v),
                                "display": tidy_string(v.name),
                                "description": tidy_string(v.description),
                                "schema_node_cls_name": k,
                            }

                            descendants_simplified.append(node_info)
                            break
                    else:
                        raise ValueError("Can't find schema in class map")

                template_context = {
                    "class_name": class_name,
                    "ref": schema_segment.ref,
                    "display": tidy_string(schema_segment.name),
                    "description": tidy_string(schema_segment.description),
                    "schema_fields": fields_simplified,
                    "descendants": descendants_simplified,
                }
                py_output += form_builder.build(template_context, "schema_tree_class.py.j2")

    py_output += form_builder.build(dict(document_footer=True), "schema_tree_class.py.j2")

    return py_output


if __name__ == "__main__":
    from builder import PROJECT_ROOT

    p = "/Users/si/Documents/TPXimpact/Projects/planning-application-data-specification"

    r = render_python(project_root=PROJECT_ROOT, planning_application_spec_path=p)
    print(r)

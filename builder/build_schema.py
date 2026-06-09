from collections import defaultdict
import csv
from functools import cached_property
import os
import warnings

from jinja2 import Environment, FileSystemLoader

from builder.planning_app_data_spec import (
    ComponentResolved,
    Field,
    PlanningAppDataResolved,
    SchemaBase,
)
from schema import valid_class_name, valid_field_name, tidy_string
from schema.fields import (
    BooleanField,
    EnumField,
    EnumOption,
    RepeatedField,
    SchemaNodeField,
    StringField,
)

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


def walk_resolved_schema(schema_items):
    """
    Recursively iterate Field, ComponentResolved, ModuleResolved, ApplicationResolved yielding each
    instance with furthest from root first.

    The order is important as python classes are being used as class variables so must be declared
    before reference.

    This function will generate duplicate items.
    """
    for spec_item in schema_items:

        modules = getattr(spec_item, "modules", [])
        yield from walk_resolved_schema(modules)

        for field_entry in getattr(spec_item, "field_entries", []):

            if isinstance(field_entry.target, ComponentResolved):
                yield from walk_resolved_schema([field_entry.target])

        yield spec_item


def render_python(project_root, planning_application_spec_path, schema_items):
    """
    @param project_root: (str)
    @param planning_application_spec_path: (str) filesystem location of git repo
            https://github.com/digital-land/planning-application-data-specification/
    @param schema_items: (iterable of subclasses of :class:`SchemaBase`) to convert into Python
            code.
    @return: (str) Python code - see package level README.md for details on how to use this.
    """

    form_builder = FormBuilder(project_root=project_root)
    py_output = form_builder.build(dict(document_header=True), "schema_tree_class.py.j2")

    # assumption - refs are primary keys
    segment_register = defaultdict(dict)
    segment_class_map = {}  # class_name -> schema_segment
    for schema_base_item in walk_resolved_schema(schema_items):

        assert isinstance(schema_base_item, SchemaBase)

        if isinstance(schema_base_item, Field):
            msg = (
                "Can't render a 'Field' instance directly. Needs to be in a "
                "module/component/application"
            )
            raise ValueError(msg)

        namespace = schema_base_item.__class__.__name__
        if schema_base_item.ref in segment_register[namespace]:
            if schema_base_item != segment_register[namespace][schema_base_item.ref]:
                msg = f"Expected ref to be primary key. Failed for {schema_base_item.ref}"
                raise ValueError(msg)

            # this schema_base_item has already been built
            continue

        # just to ensure ref is a primary key within the namespace (type of spec file)
        segment_register[namespace][schema_base_item.ref] = schema_base_item

        fields_simplified = []
        for field_entry in getattr(schema_base_item, "field_entries", []):

            # field_x is a Field or Component

            field_x = field_entry.target

            field_name = valid_field_name(field_entry.origin.ref)
            if field_name in ["_ref", "_display", "_description"]:
                raise ValueError("Reserved word for schema classes found as field name.")

            field_info = {
                "ref": field_entry.origin.ref,
                "display": field_entry.origin.name,
                "description": field_entry.origin.description,
            }

            if isinstance(field_x, ComponentResolved):

                # create a 'link' to another node
                # find name of component's python class
                for py_cls_name, spec_cls in segment_class_map.items():
                    if spec_cls == field_x:
                        break
                else:
                    py_cls_name = valid_class_name(field_x.ref)
                    segment_class_map[py_cls_name] = field_x

                    # raise ValueError(f"Can't find component '{field_x.ref}' in class map")

                schema_field = SchemaNodeField(**field_info, schema_node_cls=py_cls_name)

            elif isinstance(field_x, Field):
                if field_x.datatype == "string":
                    schema_field = StringField(**field_info)
                elif field_x.datatype == "boolean":
                    schema_field = BooleanField(**field_info)
                elif field_x.datatype == "enum":
                    schema_field = build_enum_field(
                        planning_application_spec_path, field_info, field_x.codelist
                    )

                    if schema_field is None:
                        # couldn't be built, for now use a string field
                        schema_field = StringField(**field_info)
                        if SHOW_WARNINGS:
                            warnings.warn(f"TODO missing enum field for {field_x.ref}")

                else:
                    # default used for now
                    schema_field = StringField(**field_info)
                    if SHOW_WARNINGS:
                        warnings.warn(f"Unknown field type {field_x.datatype}")

            else:
                raise NotImplementedError(f"Unprocessed field: {field_x}")

            if field_entry.origin.cardinality not in [1, "1"]:
                # schema allows multiple answers for this field.

                if field_entry.origin.cardinality != "n":
                    raise NotImplementedError("TODO - number other than infinity")

                # wrap field built above
                schema_field = RepeatedField(schema_field=schema_field)

            fields_simplified.append((field_name, schema_field))

        # schema_base_item is ComponentResolved or Module or Application
        # just vanity - I don't want the namespace in the class name unless it does overlap
        class_name = valid_class_name(schema_base_item.ref)
        if class_name in segment_class_map and segment_class_map[class_name] != schema_base_item:
            class_name = valid_class_name(schema_base_item.ref + namespace)

        if class_name in segment_class_map:
            assert (
                segment_class_map[class_name] == schema_base_item
            ), f"Mismatching py class for '{class_name}'"
        else:
            segment_class_map[class_name] = schema_base_item

        # modules are a bit different as they don't have field names
        for module_entry in getattr(schema_base_item, "modules", []):

            field_name = valid_field_name(module_entry.ref)
            if field_name in ["_ref", "_display", "_description"]:
                raise ValueError("Reserved word for schema classes found as field name.")

            if field_name in [f[0] for f in fields_simplified]:
                raise ValueError(f"Module name {field_name} already used by actual field.")

            # create a 'link' to another node
            # find name of component's python class
            for py_cls_name, spec_cls in segment_class_map.items():
                if spec_cls == module_entry:
                    break
            else:
                py_cls_name = valid_class_name(module_entry.ref)
                segment_class_map[py_cls_name] = module_entry

            field_info = {
                "ref": module_entry.ref,
                "display": module_entry.name,
                "description": module_entry.description,
            }
            schema_field = SchemaNodeField(**field_info, schema_node_cls=py_cls_name)
            fields_simplified.append((field_name, schema_field))

        template_context = {
            "class_name": class_name,
            "ref": schema_base_item.ref,
            "display": tidy_string(schema_base_item.name),
            "description": tidy_string(schema_base_item.description),
            "schema_fields": fields_simplified,
            "descendants": [],  # descendants_simplified,
        }
        py_output += form_builder.build(template_context, "schema_tree_class.py.j2")

    py_output += form_builder.build(dict(document_footer=True), "schema_tree_class.py.j2")

    return py_output


def build_enum_field(planning_application_spec_path, field_info, codelist):
    """
    Utility function to build :class:`EnumField`

    @param planning_application_spec_path: (str(
    @param field_info: (dict) - kwargs for EnumField

    @return: EnumField or None if not possible
        - not possible if data isn't available
    """
    # there is a codelist .md file with field names, for now, I'm
    # not using this.
    csv_file = os.path.join(
        planning_application_spec_path,
        "data",
        "codelist",
        f"{codelist}.csv",
    )

    if not os.path.exists(csv_file):

        # csv_file is probably an http source"
        return None

    select_options = []
    with open(csv_file) as f:

        csv_r = csv.DictReader(f)

        if "reference" not in csv_r.fieldnames or "name" not in csv_r.fieldnames:
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
    return schema_field


if __name__ == "__main__":
    from builder import PROJECT_ROOT

    # TODO get this from local config
    p = "/Users/si/Documents/TPXimpact/Projects/planning-application-data-specification"

    specification = PlanningAppDataResolved(planning_app_repo_path=p)

    r = render_python(
        project_root=PROJECT_ROOT,
        planning_application_spec_path=p,
        schema_items=specification.all_items,
    )
    print(r)

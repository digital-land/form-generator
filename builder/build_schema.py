from collections import defaultdict, namedtuple
from functools import cached_property
import warnings

from jinja2 import Environment, FileSystemLoader

from builder import safe_literal
from builder.planning_app_data_spec import (
    ComponentResolved,
    Field,
    PlanningAppDataResolved,
    SchemaBase,
)
from schema import valid_class_name, valid_field_name, tidy_string
from schema.fields import (
    BooleanField,
    DynamicEnumField,
    EnumField,
    EnumOption,
    RepeatedField,
    SelectFilter,
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


# Structured encoding of 'required-if' type rules from the specification.
# in pseudo-code, read this as ...
#
# if value_of(switch_field) == switch_value and not value_of(subject_field):
#     .. validation fails
#
# 'switch_method_call' is an optional method on switch_field
#
# @see builder/form_templates/schema_tree_class.py.j2 for how this is used
ContraintRule = namedtuple(
    "ContraintRule",
    ("switch_field", "switch_value", "subject_field", "operand", "switch_method_call"),
    defaults=("",),
)


# Operand rule logic
class RulesOpLogic:
    # python boolean operator used to join the contained rules in generated code
    op = None

    def __init__(self, rule_message, *rules):
        self.rule_message = rule_message
        self.rules = rules


class RuleDisjunction(RulesOpLogic):
    "OR"

    op = "or"


class RuleConjunction(RulesOpLogic):
    "AND"

    op = "and"


def build_rules(field_x):
    """
    Informal structure whilst code is taking shape to specify arguments
    for template to build validation rules based on field values elsewhere
    in the schema node tree.

    @param field_x: obj with 'required*' attribs

    @return list of tuple rules.
    """
    field_rules = []

    if field_x.required_if:
        # Used to build SchemaNode.valid_node method in template

        if not isinstance(field_x.required_if, list):
            if SHOW_WARNINGS:
                msg = f"Can't build rule for {field_x.ref} - required_if isn't a list"
                warnings.warn(msg)

            return []

        for rule in field_x.required_if:
            # if bool rule

            if "value" in rule:
                # 'if' rule
                v = safe_literal(rule["value"])

                r = ContraintRule(
                    switch_field=rule["field"],
                    switch_value=v,
                    subject_field=field_x.ref,
                    operand="==",
                )
                field_rules.append(r)

            elif "in" in rule:
                # member of list
                members = [safe_literal(v) for v in rule["in"]]
                m = ", ".join(members)
                v = f"[{m}]"
                r = ContraintRule(
                    switch_field=rule["field"],
                    switch_value=v,
                    subject_field=field_x.ref,
                    operand="in",
                )
                field_rules.append(r)

            elif "operator" in rule:

                if rule["operator"] in {"empty", "not_empty"}:

                    if rule["operator"] == "not_empty":
                        op_empty = ">"
                    else:
                        op_empty = "=="

                    # empty list or string
                    # using conjunction so the field's value works with len(), e.g. string or list

                    r_none = ContraintRule(
                        switch_field=rule["field"],
                        switch_value="None",
                        subject_field=field_x.ref,
                        operand="is not",
                    )
                    r_len = ContraintRule(
                        switch_field=rule["field"],
                        switch_method_call=".__len__()",
                        switch_value=0,
                        subject_field=field_x.ref,
                        operand=op_empty,
                    )
                    msg = f"Field validation problem for: {rule['field']}"
                    r_op = RuleConjunction(msg, r_none, r_len)
                    field_rules.append(r_op)

                else:
                    if SHOW_WARNINGS:
                        o = rule["operator"]
                        msg = f"Can't build rule for {field_x.ref} - unknown operator {o}"
                        warnings.warn(msg)
                    continue

            elif "any" in rule or "all" in rule:

                logical_op = "any" if "any" in rule else "all"

                equality_rules = []

                if not isinstance(rule[logical_op], list):
                    if SHOW_WARNINGS:
                        msg = f"Can't build rule for {field_x.ref} - '{logical_op}' field isn't a list"
                        warnings.warn(msg)

                    # this continue would skip any other rules built for this field but I think
                    # that's OK as this is malformed
                    continue

                for field_eq in rule[logical_op]:

                    if "field" in field_eq:

                        if "value" in field_eq:
                            # this 'any' rule is for a field level equality
                            v = safe_literal(field_eq["value"])
                            r = ContraintRule(
                                switch_field=field_eq["field"],
                                switch_value=v,
                                subject_field=None,
                                operand="==",
                            )
                            equality_rules.append(r)

                        elif "contains" in field_eq:

                            v = safe_literal(field_eq["contains"])
                            v_members = f"[{v}]"
                            r = ContraintRule(
                                switch_field=field_eq["field"],
                                switch_value=v_members,
                                subject_field=field_x.ref,
                                operand="in",
                            )
                            equality_rules.append(r)

                        elif SHOW_WARNINGS:
                            msg = f"'any' rule without 'container' or 'value' for {field_x.ref}"
                            warnings.warn(msg)

                    elif SHOW_WARNINGS:
                        msg = f"Can't build rule for {field_x.ref} - unknown 'any' rule"
                        warnings.warn(msg)

                if len(equality_rules) > 0:
                    deduped_fields = list(set([r.switch_field for r in equality_rules]))
                    # deterministic order for tests
                    deduped_fields.sort()
                    msg_fields = ", ".join(deduped_fields)

                    if logical_op == "any":
                        msg = f"One or more matches required in field(s): {msg_fields}"
                        r_op = RuleDisjunction(msg, *equality_rules)
                    elif logical_op == "all":
                        msg = f"All fields need to match for field(s): {msg_fields}"
                        r_op = RuleConjunction(msg, *equality_rules)
                    else:
                        raise ValueError("Unknown logical operation when building rules.")

                    field_rules.append(r_op)

            else:
                if SHOW_WARNINGS:
                    warnings.warn(f"Can't build rule for {field_x.ref}")
                continue

    return field_rules


def render_python(project_root, planning_spec):
    """
    @param project_root: (str)
    @param planning_spec: (:class:`PlanningAppDataResolved` obj) to convert into Python
            code.
    @return: (str) Python code - see package level README.md for details on how to use this.
    """

    form_builder = FormBuilder(project_root=project_root)
    py_output = form_builder.build(dict(document_header=True), "schema_tree_class.py.j2")

    # assumption - refs are primary keys
    segment_register = defaultdict(dict)
    segment_class_map = {}  # class_name -> schema_segment
    for schema_base_item in walk_resolved_schema(planning_spec.schema_top_level):

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
        validation_simplified = []
        for field_entry in getattr(schema_base_item, "field_entries", []):

            # field_x is a Field or Component
            field_x = field_entry.target

            # o = getattr(field_entry.origin, "required", None)
            # t = getattr(field_entry.target, "required", None)
            # if o == True and t == False:
            #     pass
            # if o == False and t == True:
            #     pass
            #
            # print(
            #     o,
            #     t,
            #     field_entry.origin.ref,
            #     type(field_entry.origin),
            #     field_entry.target.ref,
            #     type(field_entry.target),
            # )

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

                schema_field = SchemaNodeField(**field_info, schema_node_cls=py_cls_name)

            elif isinstance(field_x, Field):

                field_rules = build_rules(field_x)
                validation_simplified.extend(field_rules)

                if field_x.datatype == "string":
                    schema_field = StringField(**field_info)
                elif field_x.datatype == "boolean":
                    schema_field = BooleanField(**field_info)
                elif field_x.datatype == "enum":
                    schema_field = build_enum_field(planning_spec, field_info, field_x.codelist)

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

            # Add field level required field constraint to any field
            if getattr(field_entry.origin, "required", False) == True:
                schema_field.required = True

            fields_simplified.append((field_name, schema_field))

            # module + component rules
            if field_entry.origin != field_entry.target:
                field_rules = build_rules(field_entry.origin)
                validation_simplified.extend(field_rules)

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
            "validation_rules": validation_simplified,
        }
        py_output += form_builder.build(template_context, "schema_tree_class.py.j2")

    py_output += form_builder.build(dict(document_footer=True), "schema_tree_class.py.j2")

    return py_output


def build_enum_field(planning_spec, field_info, codelist_ref):
    """
    Utility function to build :class:`EnumField`

    @param planning_spec: (:class:`PlanningAppDataResolved` obj)
    @param field_info: (dict) - kwargs for EnumField
    @param codelist_ref: (str)

    @return: EnumField or DynamicEnumField or None if not possible
        - not possible if data isn't available
    """
    # select options are common to both types of enum
    select_options = []
    for r in planning_spec.codelist_data(codelist_ref):
        e = EnumOption(
            key=r["reference"],
            label=r["name"],
            description=r.get("description", None),
        )
        select_options.append(e)

    if len(select_options) == 0:
        # no data , not possible to build enum, warning/exception handled elsewhere
        return None

    codelist = planning_spec.codelist[codelist_ref]
    usage_key = codelist.ref
    if codelist.usage:
        # enum field adjusts which options are available based on other values in tree

        # to become generic later
        filters = {
            "specification-profile": {
                "mhclg-core": [],
                "gla": [],
            }
        }
        for r in planning_spec.codelist_usage(codelist_ref):
            key_value = r[usage_key]
            profile_name = r["specification-profile"]
            filters["specification-profile"][profile_name].append(key_value)

        encoded_filters = []
        for profile_name, key_values in filters["specification-profile"].items():

            # option to specify which enum values are active
            f = SelectFilter(
                node="submission-details.specification-profile",
                select_values=[profile_name],
                key_values=key_values,
            )
            encoded_filters.append(f)

        schema_field = DynamicEnumField(
            select_options=select_options,
            select_filter=encoded_filters,
            **field_info,
        )

    else:
        # standard enum field
        schema_field = EnumField(select_options=select_options, **field_info)

    return schema_field


if __name__ == "__main__":
    from builder import PROJECT_ROOT

    # TODO get this from local config
    p = "/Users/si/Documents/TPXimpact/Projects/planning-application-data-specification"

    specification = PlanningAppDataResolved(planning_app_repo_path=p)

    r = render_python(
        project_root=PROJECT_ROOT,
        planning_spec=specification,
    )
    print(r)

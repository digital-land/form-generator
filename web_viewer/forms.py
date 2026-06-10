from flask_wtf import FlaskForm
from wtforms import BooleanField as WTFBooleanField
from wtforms import RadioField as WTFRadioField
from wtforms import StringField as WTFStringField

from schema.fields import BooleanField as SchemaBooleanField
from schema.fields import EnumField as SchemaEnumField
from schema.fields import RepeatedField as SchemaRepeatedField
from schema.fields import StringField as SchemaStringField
from schema.fields import SchemaNodeField as SchemaSchemaNodeField


def _map_schema_field(schema_field, label, render_kw=None):
    """
    Map a single schema field to a WTForms field.

    @param schema_field: (AbstractSchemaField)
    @param label: (str) label for the rendered field
    @param render_kw: (dict) extra attributes passed to the WTForms field
    @return: (WTForms field) or None when the field describes descendant nodes (handled
        separately as their own form card)
    """
    if isinstance(schema_field, SchemaSchemaNodeField):
        # this field describes descendants - ignore it
        return None
    elif isinstance(schema_field, SchemaBooleanField):
        return WTFBooleanField(label, render_kw=render_kw)
    elif isinstance(schema_field, SchemaStringField):
        return WTFStringField(label, render_kw=render_kw)
    elif isinstance(schema_field, SchemaEnumField):

        # Optional description field
        choices = []
        for opt in schema_field.select_options:
            opt_label = opt.label
            if opt.description:
                opt_label += f" - {opt.description}"
            choices.append((opt.key, opt_label))

        return WTFRadioField(label, choices=choices, render_kw=render_kw)
    else:
        raise ValueError("Unknown schema field can't be mapped to a WTForms field")


def schema_auto_form(schema_node_class):
    """
    @param schema_node_class: (SchemaNode)
    @return: (FlaskForm)
    """
    form_fields = {}
    for attr_name, attr_value in schema_node_class.schema_fields().items():

        if isinstance(attr_value, SchemaRepeatedField):
            # multiple values allowed - render the wrapped field once and flag it so the
            # template can offer a '+' control. Repeating is not implemented yet.
            inner = attr_value.schema_field
            label = attr_value.display or inner.display or attr_name
            wt_field = _map_schema_field(inner, label, render_kw={"data-repeated": "true"})
        else:
            label = attr_value.display or attr_name
            wt_field = _map_schema_field(attr_value, label)

        if wt_field is not None:
            form_fields[attr_name] = wt_field

    form_fields["_display"] = getattr(schema_node_class, "_display", None)
    form_fields["_description"] = getattr(schema_node_class, "_description", None)
    form_class = type(schema_node_class.__name__, (FlaskForm,), form_fields)
    return form_class


def forms_extract(forms):
    """
    Transform fields in forms into Python native data structure (i.e. dict, list, str etc.).

    Forms have a prefix like 'interest-details.ldc-owner-details.person'. Data from this form
    should be in dictionary position-
    payload['interest-details']['ldc-owner-details']['person']

    @param forms: (list of FlaskForm)
    @return: (dict)
    """

    r = {}
    for form in forms:

        # Remove hyphen added by WTForms
        prefix_full = form._prefix.removesuffix("-")
        prefix_parts = prefix_full.split(".")

        # walk through dictionary to find position for this form's data
        pointer = r
        for prefix_sub in prefix_parts[:-1]:

            if prefix_sub not in pointer:
                # defaultdict might confuse this?
                pointer[prefix_sub] = {}
            pointer = pointer[prefix_sub]

        # can't just use form.data as Repeated fields need to be lists
        d = {}
        for field in form:

            # CSRF token is a transport concern, not part of the schema payload
            if field.type == "CSRFTokenField":
                continue

            assert field.short_name not in d, "Coding assumption to not override existing"

            # SchemaRepeatedField is marked up into this attribute
            render_kw = getattr(field, "render_kw", {})
            is_repeated = render_kw and render_kw.get("data-repeated", "false") == "true"

            if is_repeated:
                d[field.short_name] = [field.data]
            else:
                d[field.short_name] = field.data

        assert prefix_parts[-1] not in pointer, "Coding assumption to not override existing"

        if len(d) > 0:
            pointer[prefix_parts[-1]] = d

    return r

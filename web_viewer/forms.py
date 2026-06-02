from flask_wtf import FlaskForm
from wtforms import BooleanField as WTFBooleanField
from wtforms import RadioField as WTFRadioField
from wtforms import StringField as WTFStringField

from schema.schema_tree import AbstractSchemaField
from schema.schema_tree import BooleanField as SchemaBooleanField
from schema.schema_tree import EnumField as SchemaEnumField
from schema.schema_tree import StringField as SchemaStringField
from schema.schema_tree import SchemaNodeField as SchemaSchemaNodeField


def schema_auto_form(schema_node_class):
    """
    @param schema_node_class: (SchemaNode)
    @return: (FlaskForm)
    """

    form_fields = {}
    for attr_name, attr_value in vars(schema_node_class).items():
        if attr_name.startswith("_") or not isinstance(attr_value, AbstractSchemaField):
            continue
        label = attr_value.display or attr_name
        if isinstance(attr_value, SchemaSchemaNodeField):
            # this field describe descendants - ignore it
            pass
        elif isinstance(attr_value, SchemaBooleanField):
            form_fields[attr_name] = WTFBooleanField(label)
        elif isinstance(attr_value, SchemaStringField):
            form_fields[attr_name] = WTFStringField(label)
        elif isinstance(attr_value, SchemaEnumField):

            # Optional description field
            choices = []
            for opt in attr_value.select_options:
                opt_label = opt.label
                if opt.description:
                    opt_label += f" - {opt.description}"
                choices.append((opt.key, opt_label))

            form_fields[attr_name] = WTFRadioField(label, choices=choices)
        else:
            raise ValueError("Unknown schema field can't be mapped to a WTForms field")

    form_fields["_display"] = getattr(schema_node_class, "_display", None)
    form_fields["_description"] = getattr(schema_node_class, "_description", None)
    form_class = type(schema_node_class.__name__, (FlaskForm,), form_fields)
    return form_class

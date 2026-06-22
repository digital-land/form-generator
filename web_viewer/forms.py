from collections import defaultdict

from flask_wtf import FlaskForm
from wtforms import BooleanField as WTFBooleanField
from wtforms import HiddenField as WTFHiddenField
from wtforms import RadioField as WTFRadioField
from wtforms import StringField as WTFStringField

from schema.fields import BooleanField as SchemaBooleanField
from schema.fields import EnumField as SchemaEnumField
from schema.fields import HiddenStringField as SchemaHiddenStringField
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
    # Note there is slightly different behaviour if schema_field is on a form which
    # is an instance vs. form that is a class

    if isinstance(schema_field, SchemaSchemaNodeField):
        # this field describes descendants - ignore it
        return None
    elif isinstance(schema_field, SchemaBooleanField):
        return WTFBooleanField(label, render_kw=render_kw)
    elif isinstance(schema_field, SchemaHiddenStringField):
        # subclass of SchemaStringField - must be checked first
        return WTFHiddenField(label, render_kw=render_kw)
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
    Build a single form from a single `SchemaNode` class.

    At this stage, no data values.

    @param schema_node: (`SchemaNode` class)
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


class FormTree:
    """
    Work with WTForms for a `SchemaNode` and all the child nodes in it's tree.

    This class is builds forms and manipulates the data within them.
    """

    def __init__(self, root_node):
        """
        @param root_node: (SchemaNode)
        """
        self.root_node = root_node

        self.loaded_values = {}

    def load(self, payload):
        """
        Set field values in a form using a schema payload.

        Don't load user values from a `Form` like this. FlaskWtf does this with POSTs.

        @param payload: (dict) @see :meth:`SchemaNode.load_payload`
        """
        if len(self.loaded_values) > 0:
            raise NotImplementedError("Doesn't support overlaying, might support new payload TBC")

        self.loaded_values = payload

    def _loaded_as_prefixed(self):
        #
        # # build a 'prefix' strings in the same format as used by WTForms
        # # these prefixes are used as an index to find a form in a collection in order
        # # lookup will contain list of tuples (str, str, mixed) - (prefix, field_name, value)
        lookup = []

        def walk(node, path):
            for key, value in node.items():
                if isinstance(value, dict):
                    child_path = f"{path}.{key}" if path else key
                    walk(value, child_path)
                else:

                    if not isinstance(key, str):
                        # this is likely to be a list
                        raise NotImplementedError("TODO - can't update repeated values")

                    # scalar leaf - WTForms prefixes carry a trailing hyphen when not empty str
                    path_wtf = f"{path}-" if path != "" else path
                    lookup.append((path_wtf, key, value))

        walk(self.loaded_values, "")

        lookup_d = defaultdict(list)
        for prefix, field_name, value in lookup:
            lookup_d[prefix].append((field_name, value))
        return lookup_d

    def collection(self):
        """
        Build all the forms corresponding the `SchemaNodes` descending from `self.root_node`.

        @return: list of `FlaskForm` in order of tree traversal
        """

        root_node = self.root_node()

        # Load data into SchemaNode - values needed here so nodes can read from the tree to make
        # validation decisions.
        if self.loaded_values:
            root_node.load_payload(self.loaded_values)

        collection = self._collection(node_cls=root_node.__class__)

        lookup_d = self._loaded_as_prefixed()
        prefix_scoreboard = set(lookup_d.keys())
        for form in collection:

            # set values given to :meth:`load`
            for key, value in lookup_d.get(form._prefix, []):

                if "-" in key:
                    # TODO form attr should come from whatever created the form field
                    key = key.replace("-", "_")

                form_field = getattr(form, key)
                form_field.data = value
                prefix_scoreboard.discard(form._prefix)

        if prefix_scoreboard:

            # if a prefix is used but the values within lookup_d aren't found a KeyError will be
            # raised above. This check is to ensure all expected prefixes have entered the key
            # check.
            unused_prefixes = ", ".join(prefix_scoreboard)
            raise ValueError(f"Unused prefixes '{unused_prefixes}'. Corresponding form not found.")

        return collection

    def _collection(self, node_cls, prefix=None):
        """
        Schema node tree traverse. Build a form from each schema node.

        Note that the class defines the tree. An object of the class may not use all fields so
        shouldn't be used to build forms. The data should be added after the tree has been built
        from the class hierarchy.

        @param node_cls: subclass os `SchemaNode`, not object
        """
        if prefix is None:
            prefix = ""

        form = schema_auto_form(node_cls)(prefix=prefix)
        results = [form]

        for schema_node_field_cls in node_cls.descendant_schema_nodes():

            node_ref = schema_node_field_cls.ref
            if node_ref is None:
                node_ref = schema_node_field_cls.schema_node_cls._ref

            if node_ref is None:
                #  and issubclass(desc_node_cls, SchemaRepeatedField):
                # node_ref = desc_node_cls.._ref
                raise NotImplementedError("TODO")

            if prefix:
                child_prefix = f"{prefix}.{node_ref}"
            else:
                child_prefix = node_ref

            # fusion nodes = user interface + specification
            # descendant_cls = descendant_node_field.schema_node_cls
            # descendant = getattr(node, descendant_node_field)
            results.extend(
                self._collection(schema_node_field_cls.schema_node_cls, prefix=child_prefix)
            )

        return results

    def as_native(self):
        """
        Transform fields in forms into Python native data structure (i.e. dict, list, str etc.).

        Forms have a prefix like 'interest-details.ldc-owner-details.person'. Data from this form
        should be in dictionary position-
        payload['interest-details']['ldc-owner-details']['person']

        @param forms: (list of FlaskForm)
        @return: (dict)
        """

        # Tidied into `flask_wtf` - forms from a POST will be populated

        r = {}
        for form in self.collection():

            # Remove hyphen added by WTForms
            prefix_full = form._prefix.removesuffix("-")

            # the root form has an empty prefix; splitting "" yields [""] which would create a
            # spurious empty-string key in the payload, so treat it as no prefix parts
            prefix_parts = prefix_full.split(".") if prefix_full else []

            # walk through dictionary to find position for this form's data
            pointer = r
            for prefix_sub in prefix_parts:

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
                    # TODO - when web forms support user adding repeated elements this section can
                    # be tidied and made more consistent. At present, fields come through as both
                    # lists (within field.data) and as just a value. Use the form field's KW markup
                    # and trust schema validation to catch errors here.
                    if isinstance(field.data, list):
                        d[field.short_name] = field.data
                    else:
                        d[field.short_name] = [field.data]

                else:
                    d[field.short_name] = field.data

            if len(d) > 0:
                for k, v in d.items():
                    pointer[k] = v

        return r

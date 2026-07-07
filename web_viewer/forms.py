from flask_wtf import FlaskForm
from wtforms import BooleanField as WTFBooleanField
from wtforms import FieldList as WTFFieldList
from wtforms import Form as WTFForm
from wtforms import FormField as WTFFormField
from wtforms import HiddenField as WTFHiddenField
from wtforms import RadioField as WTFRadioField
from wtforms import StringField as WTFStringField

from schema import SchemaValidationException
from schema.fields import BooleanField as SchemaBooleanField
from schema.fields import EnumField as SchemaEnumField
from schema.fields import HiddenStringField as SchemaHiddenStringField
from schema.fields import RepeatedField as SchemaRepeatedField
from schema.fields import StringField as SchemaStringField
from schema.fields import SchemaNodeField as SchemaSchemaNodeField


class FormFabricate:
    """
    Collection of functions to build WTForms from `schema.fields` and `SchemaNodes`.

    The class is just to wrap them into a non-module container.
    """

    @staticmethod
    def map_schema_field(schema_field, label, render_kw=None):
        """
        Map a single scalar schema field to a WTForms field.

        @param schema_field: (AbstractSchemaField) not a `SchemaNodeField` or `RepeatedField` -
            those are structural and handled by :func:`_schema_form_fields`
        @param label: (str) label for the rendered field
        @param render_kw: (dict) extra attributes passed to the WTForms field
        @return: (WTForms unbound field)
        """
        # Note there is slightly different behaviour if schema_field is on a form which
        # is an instance vs. form that is a class

        if isinstance(schema_field, SchemaBooleanField):
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

    @staticmethod
    def repeated_field_list(schema_field, attr_name):
        """
        Map a `RepeatedField` to a WTForms `FieldList`.

        A repeated field can be used multiple times; each use is an entry in the list. WTForms
        binds however many indexed entries ('{name}-0', '{name}-1', ...) arrive in a POST, so
        entries the user added in the browser are picked up without the server knowing the
        count in advance. `field.data` is a list with one item per entry.

        @param schema_field: (RepeatedField)
        @param attr_name: (str) class attribute name, used as a label fallback
        @return: (WTForms unbound FieldList)
        """
        inner = schema_field.schema_field
        label = schema_field.display or inner.display or attr_name

        if isinstance(inner, SchemaSchemaNodeField):
            # a repeated node - each entry holds the node's whole subtree as a nested form
            entry_field = WTFFormField(
                FormFabricate.schema_subform(inner.schema_node_cls), label=label
            )
        else:
            entry_field = FormFabricate.map_schema_field(inner, label)

        return WTFFieldList(entry_field, label=label, min_entries=1)

    @staticmethod
    def schema_form_fields(schema_node_class, nested):
        """
        Map the fields of a `SchemaNode` class into WTForms fields.

        @param schema_node_class: (`SchemaNode` class)
        @param nested: (bool) True when building a subform for the entries of a repeated node.
            Child nodes are then inlined as `FormField`s because the whole subtree has to live
            within the entry. When False (a top level card) child nodes are skipped - they are
            rendered as their own card. @see :meth:`FormTree._collection`
        @return: (dict) attributes for a WTForms form class
        """
        form_fields = {}
        for attr_name, attr_value in schema_node_class.schema_fields().items():

            if isinstance(attr_value, SchemaRepeatedField):
                wt_field = FormFabricate.repeated_field_list(attr_value, attr_name)
            elif isinstance(attr_value, SchemaSchemaNodeField):
                if not nested:
                    # this field describes descendants - they get their own form card
                    continue
                label = attr_value.display or attr_name
                wt_field = WTFFormField(
                    FormFabricate.schema_subform(attr_value.schema_node_cls), label=label
                )
            else:
                label = attr_value.display or attr_name
                wt_field = FormFabricate.map_schema_field(attr_value, label)

            form_fields[attr_name] = wt_field

        form_fields["_display"] = getattr(schema_node_class, "_display", None)
        form_fields["_description"] = getattr(schema_node_class, "_description", None)
        return form_fields

    @staticmethod
    def schema_subform(schema_node_class):
        """
        Build a form for a `SchemaNode` class *and all its descendants*.

        Used for the entries of a repeated node. Based on `wtforms.Form` rather than
        `FlaskForm` as enclosed forms mustn't carry their own CSRF token or re-bind the
        request's form data (the enclosing form passes it down).

        @param schema_node_class: (`SchemaNode` class)
        @return: (`wtforms.Form` class)
        """
        form_fields = FormFabricate.schema_form_fields(schema_node_class, nested=True)
        return type(schema_node_class.__name__, (WTFForm,), form_fields)

    @staticmethod
    def schema_auto_form(schema_node_class):
        """
        Build a single form from a single `SchemaNode` class.

        At this stage, no data values. Child nodes aren't included (they become their own
        form/card) except when repeated - a repeated node is a `FieldList` of subforms built
        by :func:`schema_subform`.

        @param schema_node_class: (`SchemaNode` class)
        @return: (FlaskForm)
        """
        form_fields = FormFabricate.schema_form_fields(schema_node_class, nested=False)
        return type(schema_node_class.__name__, (FlaskForm,), form_fields)

    @staticmethod
    def node_form_data(node_cls, payload):
        """
        Translate a schema payload for `node_cls` into the structure `Field.process` expects.

        Payload dictionaries are keyed by schema ref (e.g. 'phone-numbers') while form fields
        are named by class attribute (e.g. 'phone_numbers'). Both are accepted as input.

        @param node_cls: (`SchemaNode` class)
        @param payload: (dict) values for `node_cls`
        @return: (dict) the same values keyed by form field name
        """
        out = {}
        for ref, (attr_name, field) in node_cls.schema_refs().items():

            if ref in payload:
                value = payload[ref]
            elif attr_name in payload:
                value = payload[attr_name]
            else:
                continue

            out[attr_name] = FormFabricate.field_form_data(field, value)

        return out

    @staticmethod
    def field_form_data(schema_field, value):
        """
        @see :func:`_node_form_data` - scalars pass through unchanged, node values are
        translated recursively.
        """
        if isinstance(schema_field, SchemaSchemaNodeField):
            return FormFabricate.node_form_data(schema_field.schema_node_cls, value)

        if isinstance(schema_field, SchemaRepeatedField) and isinstance(
            schema_field.schema_field, SchemaSchemaNodeField
        ):
            node_cls = schema_field.schema_field.schema_node_cls
            return [FormFabricate.node_form_data(node_cls, item) for item in value]

        return value

    @staticmethod
    def is_blank(value):
        """
        Whether `value` carries no information from the user - an unfilled input, an unticked
        box or a structure made entirely of these.

        @param value: native python value (dict, list or scalar)
        @return: (bool)
        """
        if isinstance(value, dict):
            return all(FormFabricate.is_blank(v) for v in value.values())
        if isinstance(value, list):
            return all(FormFabricate.is_blank(v) for v in value)
        return value is None or value is False or value == ""

    @staticmethod
    def prune_blank_entries(value):
        """
        Remove blank entries from repeated fields/nodes (i.e. lists), recursively.

        A blank entry is typically the 'add another' template entry the user didn't fill in.
        Scalars pass through unchanged - the schema decides what empty means for single
        fields.

        @param value: native python value (dict, list or scalar)
        @return: same structure as `value` with blank list entries removed
        """
        if isinstance(value, dict):
            return {k: FormFabricate.prune_blank_entries(v) for k, v in value.items()}
        if isinstance(value, list):
            return [
                FormFabricate.prune_blank_entries(v) for v in value if not FormFabricate.is_blank(v)
            ]
        return value


class FormTree:
    """
    The link between WTForms and the tree of SchemaNodes.

    Uses FormFabricate to build HTML forms and manipulates the data within them including the
    loading of initial data and extracting user entered form entry data from the forms.
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

    def collection(self):
        """
        Build all the forms corresponding the `SchemaNodes` descending from `self.root_node`.

        @return: list of `FlaskForm` in order of tree traversal
        """

        root_node = self.root_node()

        # Load data into SchemaNode - values needed here so nodes can read from the tree to make
        # validation decisions.
        if self.loaded_values:
            key_errors = root_node.set_payload(self.loaded_values)
            if key_errors:
                raise SchemaValidationException(key_errors)

        return self._collection(
            node_cls=root_node.__class__, node_obj=root_node, payload=self.loaded_values
        )

    def _collection(self, node_cls, node_obj, prefix=None, out_of_scope=False, payload=None):
        """
        Schema node tree traverse. Build a form from each schema node.

        The schema node *class* defines the tree, the schema node *object* holds data. This is
        because the class defines what is possible and the object will be equal or less than this.

        Data in the tree is used to make validation and field scope decisions. Fields that are 'out
        of scope' shouldn't be shown to the user.

        @param node_cls: subclass of `SchemaNode`, not object - defines the form structure
        @param node_obj: (SchemaNode) loaded instance of `node_cls`.
        @param out_of_scope: (bool) True when an ancestor node put this whole node out of scope.
            The form (and its descendants) are flagged so the template skips rendering them.
        @param payload: (dict) values given to :meth:`load` belonging to this node. Applied
            after construction so they override anything the form bound from a POST.
        """
        if prefix is None:
            prefix = ""
        if payload is None:
            payload = {}

        form = FormFabricate.schema_auto_form(node_cls)(prefix=prefix)

        # Fields/nodes the loaded context puts out of scope. These are flagged rather than removed
        # so the structure stays defined by the class; the template skips flagged fields and cards.
        descoped_refs = node_obj.out_of_scope_fields
        form._out_of_scope = out_of_scope

        results = [form]

        for ref, (attr_name, field) in node_cls.schema_refs().items():

            descoped = ref in descoped_refs
            loaded_value = payload.get(ref, payload.get(attr_name))

            if isinstance(field, SchemaSchemaNodeField):
                # fusion nodes = user interface + specification
                child_prefix = f"{prefix}.{ref}" if prefix else ref
                results.extend(
                    self._collection(
                        field.schema_node_cls,
                        node_obj=getattr(node_obj, attr_name),
                        prefix=child_prefix,
                        out_of_scope=out_of_scope or descoped,
                        payload=loaded_value or {},
                    )
                )
                continue

            # every other field kind (repeated nodes included) lives on this node's form
            if loaded_value is not None:
                # `process` handles every field type, including rebuilding the entries of a
                # `FieldList` from a list of values
                wt_field = form[attr_name]
                if isinstance(wt_field, WTFFieldList):
                    # FieldList.process empties `entries` but keeps counting `last_index`
                    # from the construction-time entries; reset so entries are 0-indexed
                    wt_field.last_index = -1
                wt_field.process(None, FormFabricate.field_form_data(field, loaded_value))

            if descoped:
                # flag it so the template drops it from the visible fields
                wt_field = form[attr_name]
                render_kw = dict(wt_field.render_kw or {})
                render_kw["data-out-of-scope"] = "true"
                wt_field.render_kw = render_kw

        return results

    def as_native(self):
        """
        Transform fields in forms into Python native data structure (i.e. dict, list, str etc.).

        Forms have a prefix like 'interest-details.ldc-owner-details.person'. Data from this form
        should be in dictionary position-
        payload['interest-details']['ldc-owner-details']['person']

        Repeated fields/nodes are lists with one item per entry. Entries the user left
        entirely blank carry no information so are dropped.

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

            d = {}
            for field in form:

                # CSRF token is a transport concern, not part of the schema payload
                if field.type == "CSRFTokenField":
                    continue

                assert field.short_name not in d, "Coding assumption to not override existing"

                # a FieldList's data is a list (one item per entry), a FormField's is a
                # dict - both are already the payload's shape
                d[field.short_name] = FormFabricate.prune_blank_entries(field.data)

            if len(d) > 0:
                for k, v in d.items():
                    pointer[k] = v

        return r

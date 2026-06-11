from collections import namedtuple

from . import SchemaValidationException, tidy_string


class AbstractSchemaField:
    def __init__(self, ref=None, display=None, description=None):
        """
        @param ref: (str) - name from specification/schema
        @param display: (str) - name of field suitable for user interface and display to user
        @param description: (str) - also safe to show user, details on how field is used
        """
        self.ref = ref
        self.display = display
        self.description = description

        # used by nodes to find values from other parts of the tree. Field also needs this as
        # :class:`SchemaNodeField` creates nodes. Slightly breaking open closed principal.
        # parent is only known when a value is set (i.e. scope of descriptor) so this will
        # be None before use.
        # is subclass of :class:`SchemaNode`
        self._parent_node = None

    def __set_name__(self, owner, name):
        self._descriptor_name = name

    def __get__(self, instance, instance_class=None) -> object:
        if instance is None:
            # class method called.
            # This means `self` is currently an attribute of the class (so NOT an instance
            # variable).
            #
            # see https://docs.python.org/3/howto/descriptor.html
            return self

        if self._descriptor_name not in instance.__dict__:
            # empty node - this avoids key errors when finding a value within the tree that isn't
            # set.
            self.__set__(instance, None)

        return instance.__dict__.get(self._descriptor_name)

    def __set__(self, instance, value) -> None:
        self._parent_node = instance
        instance.__dict__[self._descriptor_name] = self.prepare_value(value)

    def prepare_value(self, value):
        """
        Coerce a user supplied value into the value stored on the node.

        Default behaviour stores the value unchanged. Subclasses representing nested structures
        or where validation is needed override this.

        @return: value to store on the node instance
        """
        return value

    def _common_construction_params(self) -> dict:
        """
        Helper for __repr__ for sub-classes.

        @return: (dict) - constructor values used by all subclasses
        """
        # required field
        r = []

        if self.ref is not None:
            r.append(f'ref="{tidy_string(self.ref)}"')

        if self.display is not None:
            r.append(f'display="{tidy_string(self.display)}"')

        if self.description is not None:
            r.append(f'description="{tidy_string(self.description)}"')

        return r

    def __repr__(self) -> str:

        construction_kwargs_composite = (
            self._common_construction_params() + self._subclass_construction_params()
        )
        construction_s = ", ".join(construction_kwargs_composite)
        r = f"{self.__class__.__name__}({construction_s})"
        return r

    def _subclass_construction_params(self):
        """
        Hook method can be implemented by subclasses if they have custom construction args.
        @return: (list of str) as construction key word arguments.
        """
        return []


class StringField(AbstractSchemaField):
    def __init__(self, **kwargs):
        """
        Additional args-
            max_length (int) - TODO , not yet in use
        """

        self.max_length = kwargs.pop("max_length", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        if self.max_length is None:
            # default not needed
            return []
        return [f"max_length={self.max_length}"]


class BooleanField(AbstractSchemaField):
    pass


EnumOption = namedtuple("EnumOption", ("key", "label", "description"))


class EnumField(AbstractSchemaField):

    def __init__(self, **kwargs):
        """
        Additional args-
            select_options (list of `EnumOption`)
        """

        self.select_options = kwargs.pop("select_options", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):

        kw_pairs = []
        vt = []
        for vx in self.select_options:
            assert isinstance(vx, EnumOption)
            vt.append(repr(vx))

        vtt = ", ".join(vt)
        kw_pairs.append(f"select_options=[{vtt}]")

        return kw_pairs


class SchemaNodeField(AbstractSchemaField):
    """
    Descendant node is represented as a field.

    Needs to be a field as these are used as class variables which need to be handled slightly
    differently to instance variables.
    """

    def __init__(self, **kwargs):
        """
        Additional args-
            schema_node_cls (subclass of :class:`AbstractSchemaField` or str naming a subclass)
                - class not instance
                - str is used when the class itself isn't available for example, it's out of
                  scope. An exception will be raised if this hasn't been resolved when an attempt
                  to use the class is made.
                  It's a useful feature as it allows repr() to be used on a SchemaNodeField. See
                  :func:`builder.build_schema.render_python`.
        """

        self.schema_node_cls = kwargs.pop("schema_node_cls", None)
        if self.schema_node_cls is None:
            raise ValueError("schema_node_cls is a required value")

        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        if isinstance(self.schema_node_cls, str):
            return [f"schema_node_cls={self.schema_node_cls}"]
        return [f"schema_node_cls={self.schema_node_cls.__name__}"]

    def prepare_value(self, value):
        """
        Load dictionary of values into child node.

        @param value: (dict or None) - None means empty node, don't load payload
        """
        if value is not None and not isinstance(value, dict):
            raise SchemaValidationException([f"Field '{self.ref}' expects an object"])

        node = self.schema_node_cls()

        if value:
            node.load_payload(value)

        # relay field's parent to new node
        node._parent_node = self._parent_node

        return node


class RepeatedField(AbstractSchemaField):
    """
    Used when multiple responses can be supplied for a single field.

    `RepeatedField` holds another field (subclass of :class:`AbstractSchemaField`).
    """

    def __init__(self, **kwargs):
        """
        Additional args-
            schema_field (instance of subclass of :class:`AbstractSchemaField`)
        """

        self.schema_field = kwargs.pop("schema_field", None)
        if self.schema_field is None:
            raise ValueError("schema_field is a required value")

        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        r = repr(self.schema_field)
        return [f"schema_field={r}"]

    def prepare_value(self, value):
        """
        Load a list of values, each conforming to `self.schema_field`.
        """
        if not isinstance(value, list):
            field_ref = self.ref or self.schema_field.ref
            raise SchemaValidationException([f"Field '{field_ref}' expects a list of values"])

        loaded = []
        failure_reasons = []
        for item in value:
            try:
                loaded.append(self.schema_field.prepare_value(item))
            except SchemaValidationException as e:
                failure_reasons.extend(e.reasons)

        if failure_reasons:
            raise SchemaValidationException(failure_reasons)

        return loaded

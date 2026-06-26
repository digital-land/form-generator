from collections import namedtuple


from . import SchemaValidationException, tidy_string


class AbstractSchemaField:
    def __init__(self, ref=None, display=None, description=None, required=False):
        """
        @param ref: (str) - name from specification/schema
        @param display: (str) - name of field suitable for user interface and display to user
        @param description: (str) - also safe to show user, details on how field is used
        """
        self.ref = ref
        self.display = display
        self.description = description
        self.required = required

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
            self._parent_node = instance
            v = self.empty_value()
            instance.__dict__[self._descriptor_name] = self.prepare_value(v)

        return instance.__dict__.get(self._descriptor_name)

    def __set__(self, instance, value) -> None:
        """
        This is how descriptors are assigned values.

        The value isn't validated as legal. See :meth:`validate`.
        """
        self._parent_node = instance
        instance.__dict__[self._descriptor_name] = self.prepare_value(value)

    @property
    def _value(self):
        """
        External use of the field should use `node.attrib_name` access to descriptor's value.

        This is a convenience for internal use and it has a difference: it raises a KeyError
        exception when the value hasn't been initiated.
        """
        if self._parent_node is None:
            raise ValueError("Tree not initiated, use .shake_tree")

        current_value = self._parent_node.__dict__[self._descriptor_name]
        return current_value

    def validate(self):
        """
        Hook to be optionally implemented by subclasses for performing field level validation checks.

        TBC - When this is called the whole tree will have been loaded.

        @see :meth:`SchemaNode.valid_node` for node level validation.

        @return: None
         or
        @raise SchemaValidationException
        """
        if self.required and self._value is None:
            raise SchemaValidationException([f"Field '{self.ref}' is required"])
        return

    def empty_value(self):
        """
        The `value` that could be passed to :meth:`prepare_value` to populate the data structure
        returned by :meth:`empty_value`.

        @return mixed
        """
        return None

    @property
    def _is_empty(self):
        return self._value == self.empty_value()

    def prepare_value(self, value):
        """
        Coerce a user supplied value into the value stored on the node.

        Values stored on the parent object (by way of `AbstractSchemaField`s being descriptors)
        sometimes need an internal structure. This method can be overridden by subclasses to build
        these container structures.

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

        if self.required == True:
            r.append("required=True")

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

    def validate(self):
        super().validate()
        # None already checked in super()
        if self.required and self._value == "":
            raise SchemaValidationException([f"Field '{self.ref}' is required"])

        return


class HiddenStringField(StringField):
    """
    Mark a value as being invisible to user interface but does have a value
    """

    pass


class BooleanField(AbstractSchemaField):
    pass


EnumOption = namedtuple("EnumOption", ("key", "label", "description"))


class EnumField(AbstractSchemaField):

    def __init__(self, **kwargs):
        """
        Additional args-
            select_options (list of `EnumOption`)
        """

        self._select_options = kwargs.pop("select_options", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):

        vt = []
        for vx in self._select_options:
            assert isinstance(vx, EnumOption)
            vt.append(repr(vx))

        vtt = ", ".join(vt)
        kw_pairs = [f"select_options=[{vtt}]"]

        return kw_pairs

    @property
    def select_options(self):
        """
        Hook method that can be overridden by subclasses as an easy way to filter available
        select options.

        Typically a subclass could consider other parts of the shema node tree in order to
        change available options.

        @return (list of `EnumOption`)
        """
        return self._select_options


# SelectFilter
# - schema node location, dotted notation of ref, not class attribute
# - values this should contain
# - EnumOption keys that are active if values union with schema node values have items
# e.g.
# ("submission.specification_profile", ["core"], ["a", "b"]),
SelectFilter = namedtuple("SelectFilter", ("node", "select_values", "key_values"))


class DynamicEnumField(EnumField):
    """
    Values in fields within the tree (that this field sits in) can be used to change the options
    available.
    """

    def __init__(self, **kwargs):
        """
        Additional args-
            select_filter (list of `SelectFilter`)
        """

        self.select_filter = kwargs.pop("select_filter", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):

        kw_pairs = super()._subclass_construction_params()

        vt = []
        for vx in self.select_filter:
            assert isinstance(vx, SelectFilter)
            vt.append(repr(vx))

        vtt = ", ".join(vt)
        kw_pairs.append(f"select_filter=[{vtt}]")

        return kw_pairs

    @property
    def select_options(self):
        """
        Only return contact preferences that have been given a value in the current node.

        @see :meth:`EnumField.select_options`
        """
        # default behaviour is to return all options. This will happen when a SchemaNode class
        # (as opposed object) is built into a form.
        if self._parent_node is None:
            return self._select_options

        selected_keys = set()
        for s_filter in self.select_filter:

            if "[" in s_filter.node:
                msg = "TODO: list indicies not yet supported."
                raise NotImplementedError(msg)

            # traverse to that bit of the schema tree
            sub_tree = self._parent_node._root_node
            node_ref_parts = s_filter.node.split(".")
            for node_ref in node_ref_parts[:-1]:
                sub_tree = sub_tree[node_ref]

            node_value = sub_tree[node_ref_parts[-1]]

            if isinstance(node_value, list):
                raise NotImplementedError("TODO: just needs checking; intersection already used")

            # intersection
            overlap = set([node_value]) & set(s_filter.select_values)
            if len(overlap) > 0:
                # node values have something in common with target values so include keys
                selected_keys |= set(s_filter.key_values)

        sub_set = []
        for option in self._select_options:

            if option.key in selected_keys:
                sub_set.append(option)

        return sub_set


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

    def validate(self):
        """ """
        super().validate()
        node = self._value
        node.valid_node()

    def empty_value(self):
        return {}
        # node = self.schema_node_cls(parent_node=self._parent_node)
        # return node

    @property
    def _is_empty(self):
        try:
            _node = self._value
        except (KeyError, AttributeError):
            return True
        return False

    def prepare_value(self, value):
        """
        Load dictionary of values into child node.

        @param value: (`SchemaNode`)
        """
        # current value
        try:
            node = self._value
        except (KeyError, AttributeError):
            # it's new
            node = self.schema_node_cls(parent_node=self._parent_node)

        # just key errors
        failure_reasons = node.set_payload(value)
        if failure_reasons:
            raise SchemaValidationException(failure_reasons)

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

        if self.schema_field._parent_node is not None:
            msg = "Coding error, child type can't have a parent before repeated constructor"
            raise ValueError(msg)

        # hold's instantiated field when needed for tree traversal at class level (no values)
        self.empty_schema_field = None

        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        r = repr(self.schema_field)
        return [f"schema_field={r}"]

    def empty_value(self):

        # empty repeated field is an empty list. This list is assigned by the __get__ of the
        # descriptor to the parent instance. `self.schema_field`'s values will go in a list.
        return []

    def prepare_value(self, value):
        """
        Load a list of values, each conforming to `self.schema_field`.
        """
        if not isinstance(value, list):
            field_ref = self.ref or self.schema_field.ref
            raise SchemaValidationException([f"Field '{field_ref}' expects a list of values"])

        # repeated fields are like flat branches, they all share a parent. They all use this
        # single schema_field as values are stored (by the descriptor) on the parent object.
        # The parent_node is probably already set.
        self.schema_field._parent_node = self._parent_node

        # Existing list (if there is one in _current_value) is dropped
        loaded = self.empty_value()
        failure_reasons = []
        for item in value:
            try:

                # value to store in parent's __dict__
                field_val = self.schema_field.prepare_value(item)
                loaded.append(field_val)

            except SchemaValidationException as e:
                failure_reasons.extend(e.reasons)

        if failure_reasons:
            raise SchemaValidationException(failure_reasons)

        return loaded

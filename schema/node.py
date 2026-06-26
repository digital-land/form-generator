from . import SchemaValidationException
from .fields import AbstractSchemaField, RepeatedField, SchemaNodeField


class SchemaNode:
    """
    Abstract class to represent a grouping of fields and their validation logic in the schema tree.
    """

    # To be overridden by subclasses
    _ref = None
    _display = None
    _description = None

    def __init__(self, parent_node=None):
        # is subclass of :class:`SchemaNode`
        self._parent_node = parent_node

        # build empty tree - TBC if this should be during construction or on demand.
        self.shake_tree()

    @classmethod
    def schema_fields(cls):
        """
        @return: (dict) (str : cls) of attribute name : subclass of :clas:`AbstractSchemaField`
        """
        # multiple inheritance so can't use vars() or __dict__
        sf = {}
        for cls_att in dir(cls):
            v = getattr(cls, cls_att)
            if isinstance(v, AbstractSchemaField):
                sf[cls_att] = v

        return sf

    @classmethod
    def schema_refs(cls):
        """
        field.ref doesn't always match the class attribute. i.e. hyphens in refs can't be Python
        variables.

        @return dict with field refs as keys and tuple (class_attr, AbstractSchemaField) as value
        """
        r = {}
        for attr_name, f in cls.schema_fields().items():

            ref = f.ref

            if ref is None and isinstance(f, RepeatedField):
                ref = f.schema_field.ref

            if ref is None:
                ref = attr_name

            r[ref] = (attr_name, f)
        return r

    @classmethod
    def descendant_schema_nodes(cls):
        """
        @return: list of `SchemaNodeField` for nodes that are direct descendants of current node
        or repeated and direct.
        """
        descendants = []
        for field_attr in cls.schema_fields().values():
            if isinstance(field_attr, SchemaNodeField):
                descendants.append(field_attr)
            elif isinstance(field_attr, RepeatedField) and isinstance(
                field_attr.schema_field, SchemaNodeField
            ):
                descendants.append(field_attr.schema_field)

        return descendants

    def load_payload(self, payload):
        """
        Recursive resolve
        @return None
        @raise :class:`SchemaValidationException` is payload doesn't conform to schema
        """

        # TODO - there is an ambiguity here that needs a tidy - either ref of class attribute
        # could be in the payload. Really it should be just ref. That way the payload is more
        # closely aligned with the specification.

        payload_keys_visited = set()
        payload_fieldset = {}
        schema_fieldset = {}  # fields not in payload
        for ref, (attr_name, field) in self.schema_refs().items():

            if ref in payload:
                payload_keys_visited.add(ref)
                v = payload[ref]
                payload_fieldset[ref] = v

            elif attr_name in payload:
                payload_keys_visited.add(attr_name)
                v = payload[attr_name]
                payload_fieldset[attr_name] = v

            else:
                # .valid_update() for field not supplied in payload but is part of node
                # print("scope: ", ref)
                v = field.empty_value()
                schema_fieldset[ref] = v

        unused_payload_keys = set(payload.keys()) - payload_keys_visited
        for k in unused_payload_keys:
            payload_fieldset[k] = payload[k]

        failure_reasons = []

        try:
            field_failures = self.set_payload(payload_fieldset)
            failure_reasons.extend(field_failures)
        except SchemaValidationException as e:
            failure_reasons.extend(e.reasons)

        # child nodes will be validated via the `SchemaNodeField` on their parent being
        # called with :meth:`validate`
        try:
            self.valid_node()
        except SchemaValidationException as e:
            failure_reasons.extend(e.reasons)

        traverse_failures = self.validate_traverse()
        failure_reasons.extend(traverse_failures)

        # for fieldset, check_scope in [(payload_fieldset, False), (schema_fieldset, True)]:
        #     for k, v in fieldset.items():
        #
        #         if check_scope and k in self.out_of_scope_fields:
        #             print("continue for ", k)
        #             continue
        #
        #         try:
        #             # `__setitem__` resolves the key to a field and routes through the descriptor
        #             #  so the value is validated
        #             self[k] = v
        #         except KeyError as e:
        #             # Reverse the onus so it makes sense for user
        #             # e.g.
        #             # Field 'modules' not found in 'submission-details'
        #             # to
        #             # Field 'modules' not expected in 'submission-details'
        #             msg = e.args[0].replace(" not found in ", " not expected in ")
        #             failure_reasons.append(msg)
        #         except SchemaValidationException as e:
        #             # descendant fields validate their own values; aggregate their reasons
        #             failure_reasons.extend(e.reasons)

        # at this point all recursive building is done, nodes and fields are populated so run
        # node level checks

        if len(failure_reasons) > 0:
            raise SchemaValidationException(failure_reasons)

    def set_payload(self, payload):
        """
        Assign values to nodes and fields.

        @param payload: (dict)
        @return: (list of str) - validation failure messages limited to missing keys only
        """
        failure_reasons = []
        for k, v in payload.items():

            try:
                # `__setitem__` resolves the key to a field and routes through the descriptor
                #  so the value is validated
                self[k] = v
            except KeyError as e:
                # Reverse the onus so it makes sense for user
                # e.g.
                # Field 'modules' not found in 'submission-details'
                # to
                # Field 'modules' not expected in 'submission-details'
                msg = e.args[0].replace(" not found in ", " not expected in ")
                failure_reasons.append(msg)

        return failure_reasons

    def validate_traverse(self):
        """
        @return: list of str - reasons the tree isn't valid
        """

        def _validate(node):
            """
            @param node: (SchemaNode)
            """

            out_of_scope_fields = node.out_of_scope_fields

            failure_reasons = []
            for ref, (attr_name, field) in node.schema_refs().items():

                # ref : str - ref given to `field`
                # field : subclass of AbstractSchemaField
                # attr_name : class property/attribute name

                try:
                    field.validate()
                except SchemaValidationException as e:
                    # descendant fields validate their own values; aggregate their reasons
                    failure_reasons.extend(e.reasons)

                if ref in out_of_scope_fields and not field._is_empty:
                    failure_reasons.append(f"Field '{ref}' out of scope in '{node._ref}'")

                    # don't worry about any other issues
                    continue

                if isinstance(field, SchemaNodeField):

                    child_node = getattr(node, attr_name)
                    traverse_reasons = _validate(child_node)
                    failure_reasons.extend(traverse_reasons)

                elif isinstance(field, RepeatedField) and isinstance(
                    field.schema_field, SchemaNodeField
                ):
                    for child_node in getattr(node, attr_name):
                        traverse_reasons = _validate(child_node)
                        failure_reasons.extend(traverse_reasons)

            return failure_reasons

        failure_reasons = _validate(self)
        return failure_reasons

    def as_native(self):
        """
        Serialise this node and its descendants into native Python data structures (dict, list and
        scalars), keyed by schema ref.

        The inverse of :meth:`load_payload`; the structure mirrors the schema tree rather than the
        form layout, so this reflects what the schema actually holds.

        @return: (dict)
        """

        def native(value):
            if isinstance(value, SchemaNode):
                return value.as_native()
            if isinstance(value, list):
                return [native(item) for item in value]
            return value

        payload = {}
        for ref, (attr_name, _field) in self.schema_refs().items():
            payload[ref] = native(getattr(self, attr_name))

        return payload

    def shake_tree(self):
        """
        Walk the node tree touching every field via :func:`getattr`.

        Fields are descriptors who only see the instance they belong to when
        :meth:`AbstractSchemaField.__get__` or `__set__` is called. Walking all nodes lazily
        creates empty values, wires up `_parent_node` and instantiates descendant nodes.

        The tree needs to be in place if fields or nodes access other nodes in order to perform
        conditional validation.

        @return: None
        """

        for attr_name, field in self.schema_fields().items():

            # print(attr_name, type(field))
            #
            # if isinstance(field, RepeatedField):
            #     pass

            v = getattr(self, attr_name)

            if isinstance(field, SchemaNodeField):
                v.shake_tree()
            elif isinstance(field, RepeatedField) and isinstance(
                field.schema_field, SchemaNodeField
            ):

                # Either RepeatedField needs knowledge of SchemaNodeField or SchemaNode does.
                # I've gone with SchemaNode
                v = field.schema_field.empty_value()
                field.empty_schema_field = field.schema_field.prepare_value(v)
                field.empty_schema_field.shake_tree()

    def valid_node(self):
        """
        Hook to be optionally implemented by subclasses for performing node level checks on
        new values.

        Node level is a logical place for intra field checks.

        @see :meth:`AbstractSchemaField.valid_update` for field level validation.

        @return: None
         or
        @raise SchemaValidationException
        """
        return

    def __getitem__(self, key):
        """
        Dictionary like access to fields by their schema 'ref'.

        node.phone and node['phone-number'] should be the same thing. The former is the class
        attribute, the latter is the field's 'ref'.
        """
        refs = self.schema_refs()
        if key in refs:

            # if key in self.out_of_scope_fields:
            #     raise KeyError(f"Field '{key}' out of scope in '{self._ref}'")

            attr_name, _ = refs[key]
            return getattr(self, attr_name)

        raise KeyError(f"Field '{key}' not found in '{self._ref}'")

    def __setitem__(self, key, value):
        """
        Dictionary like assignment of a field value by its schema 'ref'.

        The mirror of :meth:`__getitem__`. The class attribute name (e.g. 'agent_reference') is
        also accepted as a key alongside the ref (e.g. 'agent-reference') so payloads built from
        web forms - whose field names are the Python attributes - resolve without translation.

        Assignment goes through the field descriptor so the value is validated.

        @raise KeyError if no field matches the key.
        @raise SchemaValidationException if the field or node rejects the value.
        """
        for ref, (attr_name, _field) in self.schema_refs().items():

            if key in (ref, attr_name):

                # if ref in self.out_of_scope_fields:
                #     raise KeyError(f"Field '{key}' out of scope in '{self._ref}'")

                setattr(self, attr_name, value)
                return

        raise KeyError(f"Field '{key}' not found in '{self._ref}'")

    def by_ref(self, path):
        """
        Resolve a dotted path of schema refs starting from this node and return the value at the
        end of it.

        e.g. node.by_ref("agent-details.agent.reference")

        @return: the value (node, list or scalar) the path points at
        @raise KeyError if any part of the path doesn't match a field
        """
        node_pointer = self
        for part in path.split("."):
            node_pointer = node_pointer[part]
        return node_pointer

    @property
    def _root_node(self):
        """
        Find the node without parents and return it.

        Public method, dunder is to differentiate with other fields as this is used as a property.

        @return: :class:`SchemaNode` - either root of tree or node specified by offset
        """
        node = self._parent_node
        if node is None:
            # current node is the root
            # this could also happen if new nodes aren't added to the tree by :class:`SchemaNodeField`
            node = self

        while True:
            if node._parent_node is None:
                # got to the top
                break

            node = node._parent_node

        return node

    @property
    def out_of_scope_fields(self):
        """
        Hook to be overridden by subclasses that use context to determine if a field can be used.

        A field that is 'out of scope' can't be read or written to.

        The context is typically the value of a field somewhere in the schema node tree.

        @return: a set of str where str is a field's `ref`
        """
        return set()


def sub_class_search(target_cls):
    """
    @return: list of subclasses of `target_cls`.
    """

    def _recurse(cls):
        for sub in cls.__subclasses__():
            yield sub
            yield from _recurse(sub)

    return list(_recurse(target_cls))

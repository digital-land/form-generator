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
        failure_reasons = []
        for k, v in payload.items():

            try:
                # `__setitem__` resolves the key to a field and routes through the descriptor so
                # the value is validated
                self[k] = v
            except KeyError as e:
                # Reverse the onus so it makes sense for user
                # e.g.
                # Field 'modules' not found in 'submission-details'
                # to
                # Field 'modules' not expected in 'submission-details'
                msg = e.args[0].replace(" not found in ", " not expected in ")
                failure_reasons.append(msg)
            except SchemaValidationException as e:
                # descendant fields validate their own values; aggregate their reasons
                failure_reasons.extend(e.reasons)

        # at this point all recursive building is done, nodes and fields are populated so run
        # node level checks
        self.valid_node()

        if len(failure_reasons) > 0:
            raise SchemaValidationException(failure_reasons)

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
        for attr_name in self.schema_fields().keys():
            value = getattr(self, attr_name)
            if isinstance(value, SchemaNode):
                value.shake_tree()

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

            if key in self.out_of_scope_fields:
                raise KeyError(f"Field '{key}' out of scope in '{self._ref}'")

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

                if key in self.out_of_scope_fields:
                    raise KeyError(f"Field '{key}' out of scope in '{self._ref}'")

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

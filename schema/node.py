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

    def __init__(self):
        # is subclass of :class:`SchemaNode`
        self._parent_node = None

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
            # when ref isn't set
            ref = f.ref or attr_name
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
        field_map = self.schema_refs()
        failure_reasons = []
        for k, v in payload.items():

            if k not in field_map:
                failure_reasons.append(f"Unknown field: '{k}'")
                continue

            # class attrib doesn't always match k
            node_att, _ = field_map.get(k)

            try:
                setattr(self, node_att, v)
            except SchemaValidationException as e:
                # descendant fields validate their own values; aggregate their reasons
                failure_reasons.extend(e.reasons)

        if len(failure_reasons) > 0:
            raise SchemaValidationException(failure_reasons)

    def __getitem__(self, key):
        """
        Dictionary like access to fields by their schema 'ref'.

        node.phone and node['phone-number'] should be the same thing. The former is the class
        attribute, the latter is the field's 'ref'.
        """
        # uses :meth:`schema_fields` so multiple inheritance safe
        for attr_name, field in self.schema_fields().items():

            # A `RepeatedField` can carry its ref on the wrapped field.
            ref = field.ref
            if ref is None and isinstance(field, RepeatedField):
                ref = field.schema_field.ref

            if ref is None:
                # class variable the `Field` is assigned to always exists
                ref = attr_name

            if ref == key:
                return getattr(self, attr_name)

        raise KeyError(f"Field '{key}' not found in '{self.__class__.__name__}'")

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


def sub_class_search(target_cls):
    """
    @return: list of subclasses of `target_cls`.
    """

    def _recurse(cls):
        for sub in cls.__subclasses__():
            yield sub
            yield from _recurse(sub)

    return list(_recurse(target_cls))

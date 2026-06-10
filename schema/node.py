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
        schema_node_cls = self.__class__
        failure_reasons = []
        for k, v in payload.items():

            try:
                schema_field = getattr(schema_node_cls, k)
            except AttributeError:
                failure_reasons.append(f"Unknown field '{k}'")
                continue

            if not isinstance(schema_field, AbstractSchemaField):
                # possible security fail if this was allowed
                failure_reasons.append(f"Attempt to set non-field value: {k}")
                continue

            try:
                setattr(self, k, v)
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

            # A `RepeatedField` carries its ref on the wrapped field.
            ref = (
                (field.ref or field.schema_field.ref)
                if isinstance(field, RepeatedField)
                else field.ref
            )
            if ref == key:
                return getattr(self, attr_name)

        raise KeyError(f"Field {key} not found in {self.__class__.__name__}")


def sub_class_search(target_cls):
    """
    @return: list of subclasses of `target_cls`.
    """

    def _recurse(cls):
        for sub in cls.__subclasses__():
            yield sub
            yield from _recurse(sub)

    return list(_recurse(target_cls))

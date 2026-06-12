import json

from schema import SchemaValidationException
from schema.node import SchemaNode


class SchemaTreeParser:
    """
    Load a serialised payload into instances of :class:`SchemaNode`. Validate if the payload
    conforms with the data schema.
    """

    def __init__(self, schema_node_cls):
        """
        :class:`SchemaNode` classes describe a tree. Each node has fields, the specialist field
        type `SchemaNodeField` represents a descendant node.

        Passing a single node to this constructor could describe a whole tree or just a group of
        fields.

        @param schema_node_cls (subclass of :class:`SchemaNode`): note this is a class, not instance
        """
        assert issubclass(schema_node_cls, SchemaNode)
        self.schema_node_cls = schema_node_cls

    def load_json(self, serialised_payload):
        """
        @param serialised_payload: (str)
        @return: (subclass of :class:`SchemaNode` obj.) recursively loaded with data.
        @raise SchemaValidationException:

        Implementation notes-
        * just JSON for now
        """
        try:
            payload = json.loads(serialised_payload)
        except json.JSONDecodeError as e:
            raise SchemaValidationException([f"Invalid JSON: {e.msg}"])

        if not isinstance(payload, dict):
            raise SchemaValidationException(["Payload is expected to be a dictionary"])

        return self.load(payload)

    def load(self, payload):
        """
        @param payload: (mixed) - probably a dict. Whatever the `schema_node_cls` is expecting.
        @return: (subclass of :class:`SchemaNode` obj.) recursively loaded with data.
        @raise SchemaValidationException:
        """
        s_node = self.schema_node_cls()

        # this will raise an exception if the payload isn't valid
        s_node.load_payload(payload)

        return s_node

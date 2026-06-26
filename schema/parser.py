import json

from schema import SchemaValidationException
from schema.node import SchemaNode


class SchemaTreeParser:
    """
    Load a serialised payload into instances of :class:`SchemaNode`. Validate if the payload
    conforms with the data schema.
    """

    def __init__(self, schema_node_cls=None):
        """
        :class:`SchemaNode` classes describe a tree. Each node has fields, the specialist field
        type `SchemaNodeField` represents a descendant node.

        Passing a single node to this constructor could describe a whole tree or just a group of
        fields.

        @param schema_node_cls (subclass of :class:`SchemaNode`): note this is a class, not instance.
                This is optional as a JSON payload passed to :meth:`load_json` will define the
                application type which is then loaded on demand.
        """
        if schema_node_cls is not None:
            assert issubclass(schema_node_cls, SchemaNode)
        self.schema_node_cls = schema_node_cls

    def load_json(self, serialised_payload, application_type_map=None):
        """
        @param serialised_payload: (str)
        @param application_type_map: (dict) str -> `SchemaNode`
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

        if self.schema_node_cls is None and application_type_map is not None:
            # set the schema_node_cls
            application_types = payload.get("submission-details", {}).get("application-types", [])
            if len(application_types) != 1 or not isinstance(application_types[0], str):
                msg = (
                    "Expecting single string in submission-details.application-types. This demo "
                    "only supports a single application type per payload. The specification "
                    "supports multiple application types per payload."
                )
                raise SchemaValidationException([msg])

            self.schema_node_cls = application_type_map.get(application_types[0])
            if self.schema_node_cls is None:
                msg = ", ".join(application_type_map.keys())
                msg = f"Unknown application ref: {application_types[0]}. Known application types: {msg}"
                raise SchemaValidationException([msg])

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

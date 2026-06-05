import unittest

from schema.parser import SchemaTreeParser, SchemaValidationException

from tests.sample_schema_nodes import ContactDetail, PhoneNumber


class TestSchemaTreeParser(unittest.TestCase):

    def test_simple_node(self):
        """
        Node without descendants.
        """
        parser = SchemaTreeParser(schema_node_cls=PhoneNumber)
        node = parser.load('{"number": "07700000000"}')
        self.assertEqual("07700000000", node.number)

    def test_invalid_json_raises(self):
        parser = SchemaTreeParser(schema_node_cls=PhoneNumber)
        with self.assertRaises(SchemaValidationException) as ctx:
            parser.load("{not valid json}")
        self.assertEqual(1, len(ctx.exception.reasons))

    def test_unknown_field(self):
        """
        A field in the payload doesn't exist in the schema
        """
        parser = SchemaTreeParser(schema_node_cls=PhoneNumber)
        with self.assertRaises(SchemaValidationException) as ctx:
            parser.load('{"colour": "red", "number": "07700000000"}')
        self.assertEqual(["Unknown field 'colour'"], ctx.exception.reasons)

    def test_set_non_abstract_schema_field(self):
        """
        Valid attrib that isn't a AbstractSchemaField shouldn't be setable.
        """
        parser = SchemaTreeParser(schema_node_cls=PhoneNumber)
        with self.assertRaises(SchemaValidationException) as ctx:
            parser.load('{"_ref": "naughty attempt to modify non-field variable"}')
        self.assertEqual(["Attempt to set non-field value: _ref"], ctx.exception.reasons)

    def test_simple_descendant(self):
        parser = SchemaTreeParser(schema_node_cls=ContactDetail)
        payload = '{"email": "me@somewhere.co.uk", "fax": {"number": "012222222"}}'
        node = parser.load(payload)
        self.assertEqual("me@somewhere.co.uk", node.email)
        # note dict and attribute access are both supported
        self.assertEqual("012222222", node.fax.number)

    def test_dict_attributes(self):
        """
        node.fax and node['fax-number'] should be the same thing. The former is the class
        attribute, the latter is the field's 'ref'. Needed because '-' is used all over the schema.
        """
        parser = SchemaTreeParser(schema_node_cls=ContactDetail)
        payload = '{"email": "me@somewhere.co.uk", "fax": {"number": "012222222"}}'
        node = parser.load(payload)
        self.assertEqual(node["fax-number"].number, node.fax.number)

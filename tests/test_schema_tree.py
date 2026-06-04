import unittest

from schema.schema_tree import SchemaNodeField, StringField
from tests.sample_schema_nodes import PhoneNumber


class TestSchemaTree(unittest.TestCase):

    def test_string_field_repr(self):
        f = StringField(ref="phone-number", display="Phone number", description="A contact number")
        # max_length arg isn't shown when None
        expected = 'StringField(ref="phone-number", display="Phone number", description="A contact number")'
        self.assertEqual(expected, repr(f))

    def test_schema_node_field_repr(self):
        f = SchemaNodeField(ref="a", schema_node_cls=PhoneNumber)
        expected = 'SchemaNodeField(ref="a", schema_node_cls=PhoneNumber)'
        self.assertEqual(expected, repr(f))

        # string representing a class that isn't in scope
        f_str_cls = SchemaNodeField(ref="a", schema_node_cls="PhoneNumber")
        expected = 'SchemaNodeField(ref="a", schema_node_cls=PhoneNumber)'
        self.assertEqual(expected, repr(f_str_cls), "Shouldn't have quotes around class name")

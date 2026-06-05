import unittest

from schema.schema_tree import (
    RepeatedField,
    SchemaNodeField,
    SchemaValidationException,
    StringField,
)
from tests.sample_schema_nodes import ContactDetail, PhoneNumber


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

    def test_repeated_field_repr(self):

        f = StringField(ref="phone-number", display="Phone number", description="A contact number")
        rf = RepeatedField(schema_field=f)

        expected = (
            "RepeatedField(schema_field="
            'StringField(ref="phone-number", display="Phone number", description="A contact number")'
            ")"
        )
        actual = repr(rf)
        self.assertEqual(expected, actual)

    def test_repeated_field_loads_list_of_nodes(self):

        node = ContactDetail()
        node.load_payload({"phones": [{"number": "111"}, {"number": "222"}]})
        self.assertEqual(["111", "222"], [p.number for p in node.phones])

    def test_repeated_field_aggregates_item_failures(self):

        with self.assertRaises(SchemaValidationException) as ctx:
            # PhoneNumber has no 'bad' field; both items should be reported
            ContactDetail().load_payload({"phones": [{"bad": "x"}, {"worse": "y"}]})

        self.assertEqual(["Unknown field 'bad'", "Unknown field 'worse'"], ctx.exception.reasons)

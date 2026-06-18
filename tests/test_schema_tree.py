import unittest

from schema import SchemaValidationException
from schema.fields import (
    EnumOption,
    RepeatedField,
    SchemaNodeField,
    StringField,
)
from tests.sample_schema_nodes import (
    ContactDetail,
    ContactPreferences,
    PhoneNumber,
    Partnership,
    FaxNumber,
)


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

        self.assertEqual(["Unknown field: 'bad'", "Unknown field: 'worse'"], ctx.exception.reasons)

    def test_schema_fields(self):

        fields = ContactDetail.schema_fields()
        expected = {"email", "fax", "phones", "contact_pref"}
        self.assertEqual(expected, set(fields))

    def test_sub_level_access(self):
        """
        A field should be able to access values elsewhere in the tree it belongs to. This is needed
        for conditional validation.
        """
        payload = {
            "person-a": {"email": "me@somewhere.co.uk", "fax-number": {"number": "0123"}},
            "person-b": {"email": "you@somewhere.co.uk", "fax-number": {"number": "4567"}},
        }
        node = Partnership()
        node.load_payload(payload)

        fax_a = node.a.fax
        self.assertEqual("0123", fax_a.number)

        root_node = fax_a._root_node
        root_field_names = set(root_node.schema_refs().keys())
        self.assertEqual({"person-a", "person-b"}, root_field_names)

        # access another node within the tree from fax_a
        fax_b = fax_a._root_node["person-b"]["fax-number"]
        self.assertEqual("4567", fax_b.number)

        # access a field value within the tree
        fax_b_number = fax_a._root_node["person-b"]["fax-number"]["number"]
        self.assertEqual("4567", fax_b_number)

        self.assertEqual(fax_b_number, fax_a._root_node.b.fax.number, "Attrib and dict access")

    def test_sub_level_access_empty_tree(self):
        """
        Same access as :meth:`test_sub_level_access` without data.
        """
        node = Partnership()

        root_node = node._root_node
        self.assertEqual(node, root_node, "Root of the root is still the root")

        root_field_names = set(root_node.schema_refs().keys())
        self.assertEqual({"person-a", "person-b"}, root_field_names)

        # access another part of the tree from fax_a
        fax_b = root_node._root_node["person-b"]["fax-number"]
        self.assertIsInstance(fax_b, FaxNumber, "Even without data it should resolve to a node")
        self.assertIsNone(fax_b.number, "Data hasn't been loaded")

    def test_custom_enum_field_repr(self):

        f = ContactPreferences(
            ref="contact-pref",
            display="Contact preference",
            select_options=[
                EnumOption(key="email", label="Email", description="Email"),
            ],
        )

        expected = (
            'ContactPreferences(ref="contact-pref", display="Contact preference",'
            " select_options=[EnumOption(key='email', label='Email', description='Email')])"
        )
        actual = repr(f)
        self.assertEqual(expected, actual)

    def test_by_ref(self):
        """
        SchemaNode().by_ref("some.path")
        """
        payload = {
            "person-a": {"email": "me@somewhere.co.uk", "fax-number": {"number": "0123"}},
            "person-b": {"email": "you@somewhere.co.uk", "fax-number": {"number": "4567"}},
        }
        node = Partnership()
        node.load_payload(payload)

        actual = node.by_ref("person-a.fax-number.number")
        self.assertEqual("0123", actual)

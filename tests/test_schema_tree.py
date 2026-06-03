import unittest

from schema.schema_tree import StringField


class TestAbstractSchemaFieldRepr(unittest.TestCase):

    def test_string_field_repr(self):
        f = StringField(ref="phone-number", display="Phone number", description="A contact number")
        # max_length arg isn't strict
        expected = 'StringField(ref="phone-number", display="Phone number", description="A contact number", max_length=None)'
        self.assertEqual(expected, repr(f))

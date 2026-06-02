"""
Simple SchemaNode examples.

These are used in unittests that confirm how the parser works. They aren't used to confirm anything
about the planning application schema.

Using real planning application schema classes might be brittle as their life-cycle is outside of
this project.

"""

from schema.schema_tree import SchemaNode, SchemaNodeField, StringField


class PhoneNumber(SchemaNode):
    _ref = "phonenumber"

    number = StringField()


class ContactDetail(SchemaNode):
    _ref = "contact-details"

    email = StringField(ref="email")
    phone = SchemaNodeField(ref="phone-number", schema_node_cls=PhoneNumber)

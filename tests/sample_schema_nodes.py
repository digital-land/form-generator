"""
Simple SchemaNode examples.

These are used in unittests that confirm how the parser works. They aren't used to confirm anything
about the planning application schema.

Using real planning application schema classes might be brittle as their life-cycle is outside of
this project.

"""

from schema.fields import RepeatedField, SchemaNodeField, StringField
from schema.node import SchemaNode


class PhoneNumber(SchemaNode):
    _ref = "phonenumber"

    number = StringField()


class FaxNumber(SchemaNode):
    _ref = "faxnumber"

    number = StringField()


class ContactDetail(SchemaNode):
    _ref = "contact-details"

    email = StringField(ref="email")
    fax = SchemaNodeField(ref="fax-number", schema_node_cls=FaxNumber)

    phones = RepeatedField(
        ref="phones",
        schema_field=SchemaNodeField(ref="phone", schema_node_cls=PhoneNumber),
    )


class Partnership(SchemaNode):
    _ref = "two-people"
    a = SchemaNodeField(ref="person-a", schema_node_cls=ContactDetail)
    b = SchemaNodeField(ref="person-b", schema_node_cls=ContactDetail)

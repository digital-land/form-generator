"""
Simple SchemaNode examples.

These are used in unittests that confirm how the parser works. They aren't used to confirm anything
about the planning application schema.

Using real planning application schema classes might be brittle as their life-cycle is outside of
this project.

"""

from schema import SchemaValidationException
from schema.fields import RepeatedField, SchemaNodeField, StringField
from schema.node import SchemaNode


# test only field
class EmailField(StringField):
    def valid_update(self, proposed_value):

        super().valid_update(proposed_value)
        if proposed_value and "@" not in proposed_value:
            raise SchemaValidationException(["Email addresses must have an @"])


class PhoneNumber(SchemaNode):
    _ref = "phonenumber"

    number = StringField()


class FaxNumber(SchemaNode):
    _ref = "faxnumber"

    number = StringField()


class ContactDetail(SchemaNode):
    _ref = "contact-details"

    email = EmailField(ref="email")
    fax = SchemaNodeField(ref="fax-number", schema_node_cls=FaxNumber)

    phones = RepeatedField(
        ref="phones",
        schema_field=SchemaNodeField(ref="phone", schema_node_cls=PhoneNumber),
    )


class Partnership(SchemaNode):
    _ref = "two-people"
    a = SchemaNodeField(ref="person-a", schema_node_cls=ContactDetail)
    b = SchemaNodeField(ref="person-b", schema_node_cls=ContactDetail)

    def valid_node(self):
        """
        Example validation check looks at a couple of places in the tree.
        """
        super().valid_node()

        r = self._root_node
        if r["person-a"].email and r["person-a"].email == r["person-b"].email:
            raise SchemaValidationException(["Duplicate email addresses"])

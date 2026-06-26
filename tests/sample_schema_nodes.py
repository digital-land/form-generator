"""
Simple SchemaNode examples.

These are used in unittests that confirm how the parser works. They aren't used to confirm anything
about the planning application schema.

Using real planning application schema classes might be brittle as their life-cycle is outside of
this project.

"""

from schema import SchemaValidationException
from schema.fields import (
    BooleanField,
    DynamicEnumField,
    EnumField,
    EnumOption,
    RepeatedField,
    SchemaNodeField,
    SelectFilter,
    StringField,
)

from schema.node import SchemaNode


# test only field
class EmailField(StringField):
    def validate(self):

        super().validate()
        email_address = self._value
        if email_address and "@" not in email_address:
            raise SchemaValidationException(["Email addresses must have an @"])


class PhoneNumber(SchemaNode):
    _ref = "phonenumber"

    number = StringField()


class FaxNumber(SchemaNode):
    _ref = "faxnumber"

    number = StringField()
    is_international = BooleanField()
    international_code = StringField()

    def valid_node(self):
        "required field depends on boolean"
        super().valid_node()
        # both dictionary and attribute access patterns work here
        reasons = []
        if self.is_international and not self.international_code:
            reasons.append("International code needed")

        if reasons:
            raise SchemaValidationException(reasons)


class ContactPreferences(EnumField):
    @property
    def select_options(self):
        """
        Only return contact preferences that have been given a value in the current node.

        @see :meth:`EnumField.select_options`
        """

        # extract values from node that are needed for decisions on select options
        node_values = {
            "fax": self._parent_node["fax-number"]["number"],
            "email": self._parent_node["email"],
            "phone": (
                self._parent_node["phones"][0]["number"]
                if len(self._parent_node["phones"]) > 0
                else None
            ),
        }

        sub_set = []
        for option in self._select_options:

            if node_values.get(option.key) is not None:
                sub_set.append(option)

        return sub_set


class ContactDetail(SchemaNode):
    _ref = "contact-details"

    email = EmailField(ref="email")
    fax = SchemaNodeField(ref="fax-number", schema_node_cls=FaxNumber)

    phones = RepeatedField(
        ref="phones",
        schema_field=SchemaNodeField(ref="phone", schema_node_cls=PhoneNumber),
    )

    contact_pref = ContactPreferences(
        ref="contact-pref",
        display="Contact preference",
        select_options=[
            EnumOption(key="email", label="Email", description="Email"),
            EnumOption(key="fax", label="Fax", description="Fax"),
            EnumOption(key="phone", label="Phone", description="Phone"),
        ],
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


class Animal(SchemaNode):
    _ref = "animal"
    keeper = SchemaNodeField(ref="keeper", schema_node_cls=ContactDetail)
    animal_name = StringField(ref="animal-name", required=True)
    where = RepeatedField(schema_field=StringField(ref="location"))
    classification = DynamicEnumField(
        ref="classification",
        display="Scientific Classification",
        select_options=[
            EnumOption(
                key="reptilia",
                label="Reptiles",
                description="",
            ),
            EnumOption(
                key="mammalia",
                label="Mammals",
                description="",
            ),
        ],
        select_filter=[
            SelectFilter(
                node="keeper.email",
                select_values=["bob@thezoo.com"],
                key_values=["reptilia"],
            ),
            SelectFilter(
                node="keeper.email",
                select_values=["tim@thezoo.com"],
                key_values=["mammalia"],
            ),
        ],
    )

    @property
    def out_of_scope_fields(self):
        de_scoped = super().out_of_scope_fields
        if self.keeper.email == "bob@thezoo.com":
            # everyone knows where Bob keeps his animals so field shouldn't be available
            return de_scoped.union({"location"})
        return de_scoped

    def valid_node(self):
        "required field depends on boolean"
        super().valid_node()

        reasons = []
        if self.keeper._parent_node is None:
            reasons.append("Example child field node should have parent_node set")

        if reasons:
            raise SchemaValidationException(reasons)

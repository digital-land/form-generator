"""
Classes to define overrides to `SchemaNode` nodes for the User Interface.

These overrides are useful for providing alternative copy.

See :func:`planning_application.schema_fusion` for how this works.

TLDR; just give classes here the same name as _specification classes you'd like to override.
"""

from schema.fields import HiddenStringField, RepeatedField

from schema.node import sub_class_search

# TODO - builder pattern would be better with fields so tiny selective over rides could be made to
# fields otherwise taken from specification.


class UserInterfaceOverride:
    pass


class Person(UserInterfaceOverride):
    _display = "A Person"


class SubmissionDetails(UserInterfaceOverride):
    application_types = RepeatedField(schema_field=HiddenStringField(ref="application-types"))
    # this one should be an enum
    planning_authority = HiddenStringField(ref="planning-authority")


all_user_interface_classes = sub_class_search(UserInterfaceOverride)

"""
Classes to define overrides to `SchemaNode` nodes for the User Interface.

These overrides are useful for providing alternative copy.

See :func:`planning_application.schema_fusion` for how this works.

TLDR; just give classes here the same name as _specification classes you'd like to override.
"""

from schema.fields import StringField

from schema.node import sub_class_search


class UserInterfaceOverride:
    pass


class Person(UserInterfaceOverride):
    _display = "A Person"


class SubmissionDetails(UserInterfaceOverride):
    application_types = StringField()
    planning_authority = StringField()


all_user_interface_classes = sub_class_search(UserInterfaceOverride)

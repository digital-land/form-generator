"""
This module provides a helper to join the planning specification Python classes (:class:`SchemaNode`)
with the user interface (UI) :class:`UserInterfaceOverride` classes.

The join is through multiple inheritance so attributes and method from the UI classes can override
those in the specification classes. This allows the specification Python classes to be generated
with simple templates that don't need to consider modifications made outside of the templating
process.

Multiple (as opposed to single) inheritance makes it easier to organise each lineage.
"""

import copy

from schema.fields import (
    AbstractSchemaField,
    DynamicEnumField,
    RepeatedField,
    SchemaNodeField,
)
from schema.planning_application_specification import all_schema_node_classes
from schema.planning_application_ui import all_user_interface_classes, UserInterfaceOverride


def schema_fusion(schema_node_classes, user_interface_classes):
    """
    A simple way to provide optional overrides to schema classes.

    Classes with the same name in .planning_application_ui and .planning_application_specification
    are auto-magiced at Python startup into classes with the same name that inherit from parents.
    This saves a load of boiler plate code that would look like this-

    ```
    from .planning_application_ui import Person as UiPerson
    from .planning_application_specification import Person as SpecificationPerson


    class Person(UiPerson, SpecificationPerson):
        pass
    ```

    The UI class is an optional. Without it just the abstract :class:`UserInterfaceOverride` class
    is used.

    @param schema_node_classes (list of subclasses of :class:`SchemaNode`)
    @param user_interface_classes (list of subclasses of :class:`UserInterfaceOverride`)

    @raise ValueError: To help developers if the UI class doesn't have a corresponding
        specification class.

    @return: dict class_name (str) : FusionClass - ready to be added to globals
    """
    r = {}
    ui_index = {cls.__name__: cls for cls in user_interface_classes}
    ui_used = set()

    for spec_cls in schema_node_classes:
        spec_cls_name = spec_cls.__name__
        ui_cls = ui_index.get(spec_cls_name)
        if ui_cls:
            # this spec class is paired with a UI class
            # e.g.
            # class _FusionCls(ui_cls, spec_cls):
            #     pass
            ui_cls_selected = ui_cls
        else:
            # just use abstract class as a UI class hasn't been defined
            # e.g.
            # class _FusionCls(UserInterfaceOverride, spec_cls):
            #     pass
            ui_cls_selected = UserInterfaceOverride

        fusion_cls = type(f"{spec_cls_name}_FusionCls", (ui_cls_selected, spec_cls), {})

        r[spec_cls_name] = fusion_cls
        ui_used.add(spec_cls_name)

    unused_ui_cls = set(ui_index.keys()) - ui_used
    if len(unused_ui_cls) > 0:
        cls_names = ", ".join(unused_ui_cls)
        raise ValueError(f"Un-matched UI classes: {cls_names}")

    for spec_cls_name, fusion_cls in r.items():

        for attr_name, field in fusion_cls.schema_fields().items():

            if isinstance(field, SchemaNodeField):

                cls_name = field.schema_node_cls.__name__

                cloned_field = copy.copy(field)
                cloned_field.schema_node_cls = r[cls_name]

                setattr(fusion_cls, attr_name, cloned_field)

            elif isinstance(field, RepeatedField) and isinstance(
                field.schema_field, SchemaNodeField
            ):
                # Repeated SchemaNodeFields

                cls_name = field.schema_field.schema_node_cls.__name__

                cloned_field = copy.copy(field)

                cloned_schema = copy.copy(field.schema_field)
                cloned_schema.schema_node_cls = r[cls_name]
                cloned_field.schema_field = cloned_schema

                setattr(fusion_cls, attr_name, cloned_field)

    return r


def planning_application_root_classes(fusion_classes):
    """
    Find all :class:`SchemaNode` (of subclasses of) nodes that are not descendants of any other.

    @param fusion_classes: (dict) class_name (str) : FusionClass

    @param param:
    @return: list of classes
    """

    referenced = set()
    for cls in fusion_classes.values():

        for schema_node_field in cls.descendant_schema_nodes():
            referenced.add(schema_node_field.schema_node_cls)

    root_spec_cls = [cls for cls in fusion_classes.values() if cls not in referenced]
    return root_spec_cls


def filter_dynamic_enums(schema_node_classes, select_value):
    """
    Find schema nodes that filter an enum field on a given specification value.

    A node qualifies if any of its fields is a :class:`DynamicEnumField` carrying a
    :class:`SelectFilter` whose `select_values` includes `select_value`.

    @param schema_node_classes: (iterable of `SchemaNode` subclasses)
    @param select_value: (str) - e.g. "gla"
    @return: (list of `SchemaNode` subclasses) preserving the input order.
    """
    matches = []

    for schema_node_class in schema_node_classes:

        for attr_name, attr_value in schema_node_class.schema_fields().items():

            if attr_name.startswith("_") or not isinstance(attr_value, AbstractSchemaField):
                continue

            # unwrap a repeated field to get at the underlying field
            field = attr_value.schema_field if isinstance(attr_value, RepeatedField) else attr_value

            if not isinstance(field, DynamicEnumField) or not field.select_filter:
                continue

            if any(select_value in s_filter.select_values for s_filter in field.select_filter):
                matches.append(schema_node_class)
                break

    return matches


def _descendant_node_classes(schema_node_class, seen=None):
    """
    Walk a schema node's subtree and collect every descendant node class.

    @param schema_node_class: (SchemaNode subclass)
    @param seen: (set) - classes already visited, guards against cycles
    @return: (list of SchemaNode subclasses) - descendants, excluding the node itself
    """
    if seen is None:
        seen = set()

    descendants = []

    for attr_name, attr_value in schema_node_class.schema_fields().items():

        if attr_name.startswith("_") or not isinstance(attr_value, AbstractSchemaField):
            continue

        # unwrap a repeated field to get at the underlying field
        field = attr_value.schema_field if isinstance(attr_value, RepeatedField) else attr_value

        if not isinstance(field, SchemaNodeField) or field.schema_node_cls in seen:
            continue

        child = field.schema_node_cls
        seen.add(child)
        descendants.append(child)
        descendants.extend(_descendant_node_classes(child, seen))

    return descendants


def schema_nodes_with_descendant(schema_node_classes, descendant_classes):
    """
    Find schema nodes whose subtree contains one of the target node classes.

    @param schema_node_classes: (iterable of SchemaNode subclasses) - nodes to test
    @param descendant_classes: (iterable of SchemaNode subclasses) - nodes to look for
    @return: (list of SchemaNode subclasses) from the first argument, preserving its order,
        which have a descendant node in `descendant_classes`.
    """
    targets = set(descendant_classes)

    matches = []
    for schema_node_class in schema_node_classes:
        descendants = _descendant_node_classes(schema_node_class)
        if any(descendant in targets for descendant in descendants):
            matches.append(schema_node_class)

    return matches


# Build multiple inheritance classes dynamically, make map of these globally available
fusion_cls_map = schema_fusion(all_schema_node_classes, all_user_interface_classes)


# add dynamically created classes to Globals so they can be imported
for spec_cls_name, fusion_cls in fusion_cls_map.items():
    globals()[spec_cls_name] = fusion_cls


# list of roots are loaded here so all the processing is done on startup not for each request.
# roots are expected to be planning application nodes
planning_application_roots = planning_application_root_classes(fusion_cls_map)

# convenience ref -> schema map
planning_application_roots_mapping = {
    fusion_node._ref: fusion_node for fusion_node in planning_application_roots
}


# schema nodes which depend on GLA option in submission-details.specification-profile
gla_nodes = filter_dynamic_enums(fusion_cls_map.values(), "gla")


# Root nodes (aka applications) which need to know about submission-details.specification-profile == 'gla'
gla_planning_app_roots = schema_nodes_with_descendant(
    schema_node_classes=planning_application_roots, descendant_classes=gla_nodes
)

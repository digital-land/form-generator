"""
This module provides a helper to join the planning specification Python classes (:class:`SchemaNode`)
with the user interface (UI) :class:`UserInterfaceOverride` classes.

The join is through multiple inheritance so attributes and method from the UI classes can override
those in the specification classes. This allows the specification Python classes to be generated
with simple templates that don't need to consider modifications made outside of the templating
process.

Multiple (as opposed to single) inheritance makes it easier to organise each lineage.
"""

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
            class _FusionCls(ui_cls, spec_cls):
                pass

        else:
            # just use abstract class as a UI class hasn't been defined
            class _FusionCls(UserInterfaceOverride, spec_cls):
                pass

        r[spec_cls_name] = _FusionCls
        ui_used.add(spec_cls_name)

    unused_ui_cls = set(ui_index.keys()) - ui_used
    if len(unused_ui_cls) > 0:
        cls_names = ", ".join(unused_ui_cls)
        raise ValueError(f"Un-matched UI classes: {cls_names}")

    return r


def planning_application_root_classes(fusion_classes, schema_node_classes):
    """
    Find all :class:`SchemaNode` subclasses that are not descendants of any other and return the
    corresponding fusion classes.

    @param fusion_classes: (dict) class_name (str) : FusionClass
    @param schema_node_classes (list of subclasses of :class:`SchemaNode`)


    @param param:
    @return: list of classes
    """

    referenced = set()
    for cls in schema_node_classes:

        if issubclass(cls, UserInterfaceOverride):
            continue

        for schema_node_cls in cls.descendant_schema_nodes():
            assert not issubclass(schema_node_cls, UserInterfaceOverride)
            referenced.add(schema_node_cls)

    root_spec_cls = [cls for cls in schema_node_classes if cls not in referenced]

    fusion_mapped = [fusion_classes[spec_cls.__name__] for spec_cls in root_spec_cls]
    return fusion_mapped


# Build multiple inheritance classes dynamically, make map of these globally available
fusion_cls_map = schema_fusion(all_schema_node_classes, all_user_interface_classes)


# add dynamically created classes to Globals so they can be imported
for spec_cls_name, fusion_cls in fusion_cls_map.items():
    globals()[spec_cls_name] = fusion_cls


# list of roots are loaded here so all the processing is done on startup not for each request.
# roots are expected to be planning application nodes
planning_application_roots = planning_application_root_classes(
    fusion_cls_map, all_schema_node_classes
)

# convenience ref -> schema map
planning_application_roots_mapping = {
    fusion_node._ref: fusion_node for fusion_node in planning_application_roots
}

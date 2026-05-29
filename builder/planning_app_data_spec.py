from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field, fields
from functools import cached_property
from glob import glob
from pathlib import Path
from typing import Any
import warnings

import frontmatter


@dataclass
class SchemaBase:
    """
    Common fields
    """

    ref: str
    name: str
    description: str
    content: str
    notes: str | None = None


@dataclass
class Field(SchemaBase):
    datatype: str | None = None
    cardinality: int | str = 1
    required: bool = False
    component: str | None = None
    codelist: str | None = None
    entry_date: str | None = None
    end_date: str | None = None
    semantics: dict | None = None
    default: Any | None = None
    date_precision: str | None = None
    parent_field: str | None = None
    typology: str | None = None
    start_date: str | None = None
    replacement_field: str | None = None


@dataclass
class ComponentBase(SchemaBase):

    entry_date: str | None = None
    end_date: str | None = None
    validation: Any | None = None
    rules: list[Rule] = field(default_factory=list)


@dataclass
class Component(ComponentBase):
    fields: list[dict] = field(default_factory=list)


@dataclass
class ComponentResolved(ComponentBase):
    field_entries: list[Field | Component] = field(default_factory=list)


@dataclass
class ModuleBase(SchemaBase):

    entry_date: str | None = None
    end_date: str | None = None
    rules: list[Rule] = field(default_factory=list)
    implementation: str | None = None


@dataclass
class Module(ModuleBase):
    fields: list[dict] = field(default_factory=list)


@dataclass
class ModuleResolved(ModuleBase):
    """
    The spec. has module -> field -> component -> group of fields

    component is a namespace as fields within the 'group of fields' could have the same name
    as a field that is directly attached to the module. So resolve fields within components.

    .field_entries need to share a list as they share an order.
    """

    field_entries: list[Field | Component] = field(default_factory=list)


@dataclass
class ApplicationBase(SchemaBase):
    extends: str | None = None
    synonyms: list[str] = field(default_factory=list)
    legislation: list[str] = field(default_factory=list)
    entry_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    modules: list[Module | dict] = field(default_factory=list)
    # components: list[Component] = field(default_factory=list)
    base_type: str | None = None
    allow_additional_properties: bool = False


@dataclass
class Application(ApplicationBase):
    fields: list[dict] = field(default_factory=list)


@dataclass
class ApplicationResolved(Application):
    """
    .field_entries need to share a list as they share an order.
    """

    field_entries: list[Field | Component] = field(default_factory=list)


@dataclass
class Rule:
    description: str
    field: str
    require: dict
    type: str  # enum? - count-constraint
    when: dict


class PlanningAppDataSpec:
    """
    Loads and exposes the planning application data specification.

    This class is a view of the spec files without interpreting the data. In particular, it
    doesn't resolve links from modules to the underlying fields and components. To do that,
    use the :class:`PlanningAppDataResolved` class.

    The specification markdown files live in a separate repository:
    https://github.com/digital-land/planning-application-data-specification

    Pass the root of that repo as `path`. Fields, components, modules, and applications are loaded
    lazily on first access.

    This module is intentionally brittle! i.e. the code should fail to process the schema if it
    doesn't match the assumptions of the developer. More info on this in the decision log.
    """

    def __init__(self, planning_app_repo_path: str | Path, hard_fail=True):
        """
        @param hard_fail: bool - raise exception if schema spec file doesn't match expected layout.
                or else warn.
        """
        self.hard_fail = hard_fail
        self.spec_dir = Path(planning_app_repo_path) / "specification"

    def _hydrate_dataclasses(self, data_cls):
        """
        Load markdown into dataclasses.

        The :class:`Application`, :class:`Component`, :class:`Field`, :class:`Module` modules
        should be as close to literal view of the underlying schema definitions held in the
        markdown files.

        Map fieldnames and warn/raise exception on mis-match.

        @param data_cls (subclass of dataclass): e.g. Field, Component, Module
        """
        expected_field_names = set([f.name for f in fields(data_cls)])
        cls_name = data_cls.__name__.lower()

        index: dict[str, data_cls] = {}
        for path in glob(str(self.spec_dir / cls_name / "*.md")):
            post = frontmatter.load(path)
            post_native = post.to_dict()

            # re-map for data class
            post_native["ref"] = post_native[cls_name]
            del post_native[cls_name]
            for k in list(post_native.keys()):
                if "-" in k:
                    py_safe_key = k.replace("-", "_")
                    post_native[py_safe_key] = post_native[k]
                    del post_native[k]

            extra_keys = set(post_native.keys()) - expected_field_names
            if len(extra_keys) > 0:
                msg = f"Unexpected attributes in {path}: " + ", ".join(list(extra_keys))
                if self.hard_fail:
                    raise ValueError(msg)
                else:
                    warnings.warn(msg)

            index[post_native["ref"]] = data_cls(**post_native)

        return index

    @cached_property
    def fields(self) -> dict[str, Field]:
        return self._hydrate_dataclasses(Field)

    @cached_property
    def components(self) -> dict[str, Component]:
        return self._hydrate_dataclasses(Component)

    @cached_property
    def modules(self) -> dict[str, Module]:
        return self._hydrate_dataclasses(Module)

    @cached_property
    def applications(self) -> dict[str, Application]:
        return self._hydrate_dataclasses(Application)


class PlanningAppDataResolved(PlanningAppDataSpec):
    """
    Take the specification loaded from the *.md schema files and interpret the relationships
    between fields. For example, resolve fields in modules.
    """

    @cached_property
    def applications(self) -> dict[str, ApplicationResolved]:

        resolved = {}
        applications = super().applications

        for app_ref, app in applications.items():

            from_schema = asdict(app)
            # difference between Application and ApplicationResolved
            del from_schema["fields"]
            app_r = ApplicationResolved(**from_schema)

            modules = [self.modules[m["module"]] for m in app.modules]

            app_r.field_entries = self.resolve_fields(app.fields)
            app_r.modules = modules

            resolved[app_ref] = app_r

        # def _resolve_inheritance(self, index: dict[str, Application]) -> None:

        for app_ref, app in resolved.items():

            if app.extends:
                parent_app = resolved[app.extends]

                assert parent_app.extends is None, "TODO: recursive version of this"

                for parent_module in parent_app.modules:
                    if parent_module not in app.modules:
                        app.modules.append(parent_module)

        return resolved

    @cached_property
    def modules(self) -> dict[str, ModuleResolved]:
        """
        Load scalar values from spec file and resolve field names into :class:`Field` and
        :class:`Component` instances.
        """
        resolved = {}
        modules = super().modules
        for module_ref, module in modules.items():

            from_schema = asdict(module)
            # difference between Module and ModuleResolved
            del from_schema["fields"]

            module_r = ModuleResolved(**from_schema)
            module_r.field_entries = self.resolve_fields(module.fields)
            resolved[module_ref] = module_r

        return resolved

    @cached_property
    def components(self) -> dict[str, ComponentResolved]:
        """
        Load scalar values from spec file and resolve field names into :class:`Field` and
        :class:`Component` instances.
        """
        resolved = {}
        components = super().components
        for component_ref, component in components.items():

            from_schema = asdict(component)
            # difference between Component and ComponentResolved
            del from_schema["fields"]

            component_r = ComponentResolved(**from_schema)

            # can't use :meth:`resolve_fields` as it would create a cycle to this method
            # could do something clever with recursion. Instead starting with a simple
            # idea - put a reference string during first iteration and resolve that
            # with an iteration of `resolved`

            fieldset = []
            for f in component.fields:
                field_ref = f["field"]
                field = self.fields[field_ref]

                if field.component:

                    assert isinstance(field.component, str), "Coding assumption"

                    component_is_ready = resolved.get(field.component)
                    if isinstance(component_is_ready, ComponentResolved):
                        component_contextualised = copy.copy(component_is_ready)
                        component_contextualised.ref = field_ref
                        fieldset.append(component_contextualised)
                    else:
                        # defer the resolution
                        fieldset.append((field_ref, field.component))
                else:
                    # normal field
                    fieldset.append(field)

            component_r.field_entries = fieldset
            resolved[component_ref] = component_r

        # Do the deferred resolution. Any strings in list of fields are referring to components
        # that weren't available during the initial build. The changes_made flag is to avoid the
        # need to build a resolution dependency chain which shouldn't be needed for data this
        # simple.

        def resolve_component(component_r):
            """
            Recursive function to find components within components and resolve them to
            :class:`ComponentResolved` objects.
            """
            changes_made = 0
            waiting = 0

            updated_fieldset = []
            for f in component_r.field_entries:
                if isinstance(f, tuple):

                    field_ref, field_component = f
                    component_is_ready = resolved.get(field_component)

                    if isinstance(component_is_ready, ComponentResolved):

                        component_contextualised = copy.copy(component_is_ready)
                        component_contextualised.ref = field_ref
                        updated_fieldset.append(component_contextualised)
                        changes_made += 1
                    else:
                        # not ready yet
                        waiting += 1
                        updated_fieldset.append(f)
                elif isinstance(f, ComponentResolved):
                    changes_made_recurse, waiting_recurse = resolve_component(f)
                    changes_made += changes_made_recurse
                    waiting += waiting_recurse
                    updated_fieldset.append(f)
                else:
                    updated_fieldset.append(f)

            component_r.field_entries = updated_fieldset

            return changes_made, waiting

        while True:

            changes_made = 0
            waiting = 0
            for component_ref, component_r in resolved.items():
                comp_changes_made, comp_waiting = resolve_component(component_r)
                changes_made += comp_changes_made
                waiting += comp_waiting

            if changes_made == 0:
                break

        if waiting > 0:
            msg = "Failed to resolve circular dependency for components"
            raise ValueError(msg)

        return resolved

    def resolve_fields(self, schema_fields):
        """
        Resolve components to fields and field names into :class:`Fields`.

        Data layout is-
        application/module -> field -> component -> group of fields

        @see doc string in :class:`Module` for more info

        @param schema_fields: (iterable of dict) as loaded from schema file.

        @return: (list) - of :class:`Field` and :class:`Component` instances. The two
            types are combined into a single list as they share an ordering.
        """

        field_entries = []
        for field_obj in schema_fields:

            # hard failure on incomplete spec. with missing references
            field_ref = field_obj["field"]
            field = self.fields[field_ref]

            if field.component:
                # resolve it
                component = self.components[field.component]
                component_contextualised = copy.copy(component)
                component_contextualised.ref = field_ref
                field_entries.append(component_contextualised)

            else:
                field_entries.append(field)

        return field_entries

from __future__ import annotations

import csv
import io
from dataclasses import asdict, dataclass, field, fields, replace
from functools import cached_property
from glob import glob
from pathlib import Path
from typing import Any
import warnings

import frontmatter
import requests


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
    required_if: list | None = None
    applies_if: list | None = None
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
    rules: list[Rule] = field(default_factory=list)
    minimum_items: int | None = None


@dataclass
class FieldLink:
    """
    A reference from a component to a field, carrying usage-level overrides.

    Distinct from :class:`Field`: a ``Field`` is the field's own definition (name,
    datatype, etc.) whereas a ``FieldLink`` is how a component *uses* that field. The
    ``field`` attribute is the referenced field's ref.

    Default should be None, i.e. all are optional. None values are skipped when Field is built
    by overriding normal `Field` with these values. See :meth:`PlanningAppDataResolved.components`.
    """

    field: str
    required: bool | None = None
    required_if: list | None = None
    applies_if: list | None = None
    description: str | None = None
    notes: str | None = None
    codelist: str | None = None
    default: Any | None = None
    name: str | None = None
    minimum_items: int | None = None


@dataclass
class ComponentBase(SchemaBase):

    entry_date: str | None = None
    end_date: str | None = None
    validation: Any | None = None
    rules: list[Rule] = field(default_factory=list)


@dataclass
class Component(ComponentBase):
    fields: list[FieldLink] = field(default_factory=list)


@dataclass
class FieldEntry:
    origin: Field
    target: "Field | ComponentResolved"


@dataclass
class ComponentResolved(ComponentBase):
    field_entries: list[FieldEntry] = field(default_factory=list)


@dataclass
class ModuleBase(SchemaBase):
    entry_date: str | None = None
    end_date: str | None = None
    rules: list[Rule] = field(default_factory=list)
    implementation: str | None = None


@dataclass
class Module(ModuleBase):
    fields: list[FieldLink] = field(default_factory=list)


@dataclass
class ModuleResolved(ModuleBase):
    field_entries: list[FieldEntry] = field(default_factory=list)


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
    fields: list[FieldLink] = field(default_factory=list)


@dataclass
class ApplicationResolved(Application):
    """
    .field_entries need to share a list as they share an order.
    """

    field_entries: list[FieldEntry] = field(default_factory=list)


@dataclass
class Rule:
    description: str
    field: str
    require: dict
    type: str  # enum? - count-constraint
    when: dict


@dataclass
class Codelist:
    ref: str
    name: str
    description: str
    content: str
    notes: str | None = None
    fields: list[dict] = field(default_factory=list)
    entry_date: str | None = None
    end_date: str | None = None
    github_discussion: str | None = None
    key_field: str | None = None
    licence: str | None = None
    organisation: str | None = None
    plural: str | None = None
    source: str | None = None
    usage: str | None = None


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

    def __init__(
        self,
        planning_app_repo_path: str | Path,
        hard_fail=True,
        spec_files_path="specification",
        allow_http_requests=True,
    ):
        """
        @param planning_app_repo_path: (str) filesystem location of git repo
            https://github.com/digital-land/planning-application-data-specification/
        @param hard_fail: bool - raise exception if schema spec file doesn't match expected layout.
                or else warn.
        @param spec_files_path: (str) - subdirectory of `planning_app_repo_path`
        """
        self.hard_fail = hard_fail
        self.allow_http_requests = allow_http_requests

        # these two are fixed-up by unittests
        self.spec_dir = Path(planning_app_repo_path) / spec_files_path
        self.spec_data = Path(planning_app_repo_path) / "data"

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
                msg += f". Should field(s) be added to the '{data_cls.__name__}' dataclass?"
                if self.hard_fail:
                    raise ValueError(msg)
                else:
                    warnings.warn(msg)

            if data_cls is Component or data_cls is Module or data_cls is Application:
                post_native["fields"] = [
                    self.build_field_link(entry, path) for entry in post_native.get("fields", [])
                ]

            index[post_native["ref"]] = data_cls(**post_native)

        return index

    def build_field_link(self, entry: dict, path: str) -> FieldLink:
        """
        Build a :class:`FieldLink` from a component's raw ``fields`` list entry.

        Nested keys aren't touched by the top-level dash->underscore remap in
        :meth:`_hydrate_dataclasses`, so normalise them here. Unexpected keys are
        treated with the same brittleness as the rest of the loader.
        """
        entry = dict(entry)
        for k in list(entry.keys()):
            if "-" in k:
                entry[k.replace("-", "_")] = entry.pop(k)

        expected_field_names = set([f.name for f in fields(FieldLink)])
        extra_keys = set(entry.keys()) - expected_field_names
        if len(extra_keys) > 0:
            e_keys = ", ".join(list(extra_keys))
            msg = (
                f"Unexpected attributes in Component Fields needed to build FieldLink in {path}: "
                f"{e_keys}. Should field(s) be added to the 'FieldLink' dataclass?"
            )
            if self.hard_fail:
                raise ValueError(msg)
            else:
                warnings.warn(msg)

        return FieldLink(**entry)

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

    @cached_property
    def codelist(self) -> dict[str, Codelist]:
        return self._hydrate_dataclasses(Codelist)

    def codelist_data(self, codelist_ref):
        """
        Generator yield (dict) for each row in CSV referenced by codelist definition
        @param codelist_ref: (str)
        """
        codelist = self.codelist[codelist_ref]

        if codelist.source.startswith("https://"):
            # remote file

            if not self.allow_http_requests:
                msg = (
                    f"Can't fetch codelist : {codelist.source}, 'allow_http_requests permissions"
                    " flag is False"
                )
                if self.hard_fail:
                    raise ValueError(msg)
                else:
                    warnings.warn(msg)

                return

            response = requests.get(codelist.source, timeout=10)
            response.raise_for_status()
            csv_r = csv.DictReader(io.StringIO(response.text))
            yield from csv_r

        else:
            # local file

            # remove overlap between repo relative path and path in codelist definition
            path_prefix = "data/"
            msg = f"Can't process codelist source : {codelist.source}"
            assert codelist.source.startswith(path_prefix), msg

            csv_path = self.spec_data / codelist.source[len(path_prefix) :]
            with open(csv_path) as f:

                csv_r = csv.DictReader(f)
                yield from csv_r

    def codelist_usage(self, codelist_ref):
        """
        Usage data determines which codelist items are active.

        Generator yield (dict) for each row in CSV referenced by codelist's usage definition
        @param codelist_ref: (str)
        """
        codelist = self.codelist[codelist_ref]

        # remove overlap between repo relative path and path in codelist definition
        path_prefix = "data/"
        msg = f"Can't process codelist source : {codelist.usage}"
        assert codelist.usage.startswith(path_prefix), msg

        csv_path = self.spec_data / codelist.usage[len(path_prefix) :]
        with open(csv_path) as f:

            csv_r = csv.DictReader(f)
            yield from csv_r


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

                for field_entry in parent_app.field_entries:
                    # TODO - correct order?
                    app.field_entries.append(field_entry)

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
                field_ref = f.field
                # apply the FieldLink's usage-level overrides onto a copy of the field
                # definition (replace avoids mutating the shared cached Field) and allows
                # the field to be used in multiple places with different (FieldLink) overrides.
                # Only override with values that were actually set on the link (not None), so
                # the field's own definition is preserved where the link is silent.
                overrides = {
                    fl_field.name: getattr(f, fl_field.name)
                    for fl_field in fields(f)
                    if fl_field.name != "field" and getattr(f, fl_field.name) is not None
                }
                field = replace(self.fields[field_ref], **overrides)

                if field.component:

                    assert isinstance(field.component, str), "Coding assumption"

                    component_is_ready = resolved.get(field.component)
                    if isinstance(component_is_ready, ComponentResolved):

                        fe = FieldEntry(origin=field, target=component_is_ready)
                        fieldset.append(fe)
                    else:
                        # defer the resolution - field.component is a str
                        fe = FieldEntry(origin=field, target=field.component)
                        fieldset.append(fe)

                else:
                    # normal field
                    fe = FieldEntry(origin=field, target=field)
                    fieldset.append(fe)

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
            for field_entry in component_r.field_entries:

                if isinstance(field_entry.target, str):

                    component_is_ready = resolved.get(field_entry.target)
                    if isinstance(component_is_ready, ComponentResolved):
                        fe = FieldEntry(origin=field_entry.origin, target=component_is_ready)
                        updated_fieldset.append(fe)
                        changes_made += 1
                    else:
                        # not ready yet
                        waiting += 1
                        updated_fieldset.append(field_entry)

                elif isinstance(field_entry.target, ComponentResolved):
                    changes_made_recurse, waiting_recurse = resolve_component(field_entry.target)
                    changes_made += changes_made_recurse
                    waiting += waiting_recurse
                    updated_fieldset.append(field_entry)
                else:
                    updated_fieldset.append(field_entry)

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
        Create `field_entries`

        Data layout is-
        application/module -> field -> component -> group of fields

        @param schema_fields: (iterable of dict) as loaded from schema file.

        @return: (list of tuples) - (field_name, x)
            where x is :class:`Field` or :class:`ComponentResolved` instances.
            field_name is as per the spec. This might not be python safe name.
        """
        field_entries = []
        for f in schema_fields:

            # hard failure on incomplete spec. with missing references
            field_ref = f.field

            # see doc. in components version of this.
            overrides = {
                fl_field.name: getattr(f, fl_field.name)
                for fl_field in fields(f)
                if fl_field.name != "field" and getattr(f, fl_field.name) is not None
            }
            field = replace(self.fields[field_ref], **overrides)

            if field.component:
                # resolve it
                component = self.components[field.component]
                fe = FieldEntry(origin=field, target=component)
                field_entries.append(fe)

            else:
                fe = FieldEntry(origin=field, target=field)
                field_entries.append(fe)

        return field_entries

    @property
    def schema_top_level(self):
        """
        Simple list of schema items to render into Python classes.

        Fields are not rendered directly into classes so are not returned directly but are
        linked to other types of item here.

        @return: (list of subclasses of `SchemaBase`)
        """
        all_spec = list(self.applications.values())
        all_spec += list(self.modules.values())
        all_spec += list(self.components.values())
        return all_spec

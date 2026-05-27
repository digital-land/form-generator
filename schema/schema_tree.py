from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any, List

from builder.planning_app_data_spec_bin.models import FieldDef
from schema import tidy_string


@dataclass
class SchemaSegment:
    """
    Node in the schema tree has name (ref from schema objects),
    """

    ref: str
    namespace: str  # ref in upstream schema's data types isn't globally unique
    name: str
    description: str
    descendants: List[Any] = field(default_factory=list)  # really it's SchemaSegment
    fields: List[FieldDef] = field(default_factory=list)


class SchemaNode:
    """
    Abstract class to represent a grouping of fields and their validation logic in the schema tree.
    """

    # To be overridden by subclasses
    _ref = None
    _display = None
    _description = None
    _descendants = []


def schema_node_root_classes():
    """
    @return: list of :class:`SchemaNode` subclasses that are not descendants of any other.
    """
    all_classes = schema_node_classes()
    referenced = set()
    for cls in all_classes:
        for descendant in getattr(cls, "_descendants", []):
            referenced.add(descendant)
    return [cls for cls in all_classes if cls not in referenced]


def schema_node_classes():
    """
    @return: list of subclasses of :class:`SchemaNode`.
    """

    def _recurse(cls):
        for sub in cls.__subclasses__():
            yield sub
            yield from _recurse(sub)

    return list(_recurse(SchemaNode))


class AbstractSchemaField:
    def __init__(self, display=None, description=None):
        """
        @param display: (str) - name of field suitable for user interface and display to user
        @param description: (str) - also safe to show user, details on how field is used
        """
        self.display = display
        self.description = description

    def _common_construction_params(self) -> dict:
        """
        Helper for __repr__ for sub-classes.

        @return: (dict) - constructor values used by all subclasses
        """
        return {"display": self.display, "description": self.description}

    def __repr__(self) -> str:

        construction_kwargs = {
            **self._common_construction_params(),
            **self._subclass_construction_params(),
        }

        kw_pairs = []
        for k, v in construction_kwargs.items():

            if v is None:
                kw_pairs.append(f"{k}={v}")

            elif isinstance(v, str):

                # clean schema strings into nicer python
                vt = tidy_string(v)
                kw_pairs.append(f'{k}="{vt}"')

            elif isinstance(v, list):

                # MAYBE TODO - recursive as well?

                vt = []
                for vx in v:
                    # TODO - breaking Law of Demeter
                    assert isinstance(vx, EnumOption)
                    vt.append(repr(vx))

                vtt = ", ".join(vt)
                kw_pairs.append(f"{k}=[{vtt}]")

            else:
                raise NotImplementedError(f"TODO: can't repr field: '{k}'")

        construction_s = ", ".join(kw_pairs)
        r = f"{self.__class__.__name__}({construction_s})"
        return r

    def _subclass_construction_params(self):
        """
        This method can be implemented by subclasses if they have custom construction args.
        @return: dict.
        """
        return {}


class StringField(AbstractSchemaField):
    def __init__(self, **kwargs):
        """
        Additional args-
            max_length (int) - TODO , not yet in use
        """

        self.max_length = kwargs.pop("max_length", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        return {"max_length": self.max_length}


class BooleanField(AbstractSchemaField):
    pass


EnumOption = namedtuple("EnumOption", ("key", "label", "description"))


class EnumField(AbstractSchemaField):

    def __init__(self, **kwargs):
        """
        Additional args-
            select_options (list of `EnumOption`)
        """

        self.select_options = kwargs.pop("select_options", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        return {"select_options": self.select_options}

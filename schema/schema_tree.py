from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any, List


from builder.planning_app_data_spec import Field
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
    fields: List[Field] = field(default_factory=list)


class SchemaValidationException(Exception):
    """
    Raised when data that doesn't conform with the schema is parsed.
    """

    def __init__(self, reasons):
        self.reasons = reasons
        super().__init__("; ".join(reasons))


class SchemaNode:
    """
    Abstract class to represent a grouping of fields and their validation logic in the schema tree.
    """

    # To be overridden by subclasses
    _ref = None
    _display = None
    _description = None

    @classmethod
    def descendant_schema_nodes(cls):
        """
        @return: list of `SchemaNode` for nodes that are descendants of current node.
        """
        descendants = []
        for cls_attr in vars(cls).values():
            if isinstance(cls_attr, SchemaNodeField):
                descendants.append(cls_attr.schema_node_cls)
        return descendants

    def load_payload(self, payload):
        """
        Recursive resolve
        @return None
        @raise :class:`SchemaValidationException` is payload doesn't conform to schema
        """
        schema_node_cls = self.__class__
        failure_reasons = []
        for k, v in payload.items():

            try:
                schema_field = getattr(schema_node_cls, k)
            except AttributeError:
                failure_reasons.append(f"Unknown field '{k}'")
                continue

            if not isinstance(schema_field, AbstractSchemaField):
                # possible security fail if this was allowed
                failure_reasons.append(f"Attempt to set non-field value: {k}")
                continue

            setattr(self, k, v)

        if len(failure_reasons) > 0:
            raise SchemaValidationException(failure_reasons)

    def __getitem__(self, key):
        """
        Dictionary like access to fields.

        node.phone and node['phone-number'] should be the same thing. The former is the class
        attribute, the latter is the field's 'ref'.
        """
        for k, v in vars(self.__class__).items():
            if isinstance(v, AbstractSchemaField) and v.ref == key:
                return getattr(self, k)

        raise KeyError(f"Field {key} not found in {self.__class__.__name__}")


def schema_node_root_classes():
    """
    @return: list of :class:`SchemaNode` subclasses that are not descendants of any other.
    """
    all_classes = schema_node_classes()
    referenced = set()
    for cls in all_classes:

        for schema_node_cls in cls.descendant_schema_nodes():
            referenced.add(schema_node_cls)

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
    def __init__(self, ref=None, display=None, description=None):
        """
        @param ref: (str) - name from specification/schema
        @param display: (str) - name of field suitable for user interface and display to user
        @param description: (str) - also safe to show user, details on how field is used
        """
        self.ref = ref
        self.display = display
        self.description = description

    def __set_name__(self, owner, name):
        self._descriptor_name = name

    def __get__(self, instance, instance_class=None) -> object:
        if instance is None:
            # class method called.
            # This means `self` is currently an attribute of the class (so NOT an instance
            # variable).
            #
            # see https://docs.python.org/3/howto/descriptor.html
            return self
        return instance.__dict__.get(self._descriptor_name)

    def __set__(self, instance, value) -> None:
        instance.__dict__[self._descriptor_name] = value

    def _common_construction_params(self) -> dict:
        """
        Helper for __repr__ for sub-classes.

        @return: (dict) - constructor values used by all subclasses
        """
        return {"ref": self.ref, "display": self.display, "description": self.description}

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


class SchemaNodeField(AbstractSchemaField):
    """
    Descendant node is represented as a field.

    Needs to be a field as these are used as class variables which need to be handled slightly
    differently to instance variables.
    """

    def __init__(self, **kwargs):
        """
        Additional args-
            schema_node_cls (subclass of :class:`AbstractSchemaField`) - class not instance
        """

        self.schema_node_cls = kwargs.pop("schema_node_cls", None)
        super().__init__(**kwargs)

    def _subclass_construction_params(self):
        return {"schema_node_cls": self.schema_node_cls.__name__}

    def __set__(self, instance, value) -> None:
        """
        Load dictionary of values into child node.
        """
        assert isinstance(value, dict), "Keys become attributes of self.schema_node_cls"

        node = self.schema_node_cls()
        node.load_payload(value)

        instance.__dict__[self._descriptor_name] = node

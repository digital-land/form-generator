from collections import namedtuple
import warnings


from builder import safe_literal


# Structured encoding of 'required-if' type rules from the specification.
# in pseudo-code, read this as ...
#
# if value_of(switch_field) == switch_value:
#     .. validation fails
#
# 'switch_method_call' is an optional method on switch_field
#
# `RulesOpLogic` supports AND and OR so multiple rules can be built into a structure.
#
# @see builder/form_templates/schema_tree_class.py.j2 for how this is used
ContraintRule = namedtuple(
    "ContraintRule",
    ("switch_field", "switch_value", "operand", "switch_method_call"),
    defaults=("",),
)

ScopedContraintRule = namedtuple(
    "ScopedContraintRule",
    ("switch_field", "switch_value", "operand", "switch_method_call", "scope_field"),
    defaults=("",),
)

# simple rule for comparison with 'Application type'. It's a simple case that doesn't easily fit
# into `ContraintRule. Note that the template+render process assumes this hasn't been wrapped in
# one of the subclasses of `RulesOpLogic`
#
# app_type_match : str holding python notation for set of str. These are the application types
#                  to compare with application type under validation.
#                  e.g. '{"non-material-amendment"}'
ApplicationTypeRule = namedtuple(
    "ApplicationTypeRule", ("switch_field", "app_type_match", "rule_message")
)


# Operand rule logic
class RulesOpLogic:
    # python boolean operator used to join the contained rules in generated code
    op = None

    def __init__(self, rule_message, *rules):
        self.rule_message = rule_message
        self.rules = rules


class RuleDisjunction(RulesOpLogic):
    "OR"

    op = "or"


class RuleConjunction(RulesOpLogic):
    "AND"

    op = "and"


class BuildConditions:
    """
    Transform conditional rules from the schema into a structure that can be more easily rendered
    into Python code using a template. @see :func:`build_schema.render_python`.
    """

    SHOW_WARNINGS = False
    EXCEPTION_ON_UNPROCESSABLE = False

    def __init__(self, application_inheritance_map=None):
        """
        @param application_inheritance_map: (dict) parent_node_ref -> list of child node refs

            The specification files use the parent node's ref. This should be substituted with all
            known child nodes.

            'base_type' applications are like non-concrete abstract classes. They aren't actual
            application types so shouldn't be in the rules. Their subclasses take the place of
            the parent.

            It would be more logical and consistent to resolve this in
            :class:`PlanningAppDataResolved` but that results in a really complex and repeated
            chunk of code as application_types are in .required_if and .applies_if ; they could
            be standalone or within a conjunction or a disjunction. The current class has already
            dealt with all that.
        """
        if application_inheritance_map:
            self.application_inheritance_map = application_inheritance_map
        else:
            self.application_inheritance_map = {}

    def log_failure(self, msg):
        """
        Alert when the specification couldn't be parsed. Either exception in strict mode or issue
        a warning and carry on parsing.
        """
        if self.EXCEPTION_ON_UNPROCESSABLE:
            raise NotImplementedError(msg)

        if self.SHOW_WARNINGS:
            warnings.warn(msg)

    def required_if_rules(self, field_x):
        """
        Build validation rules used by the template to create the `SchemaNode.valid_node` method.

        The validation rules use field values from elsewhere in the schema node tree.

        @param field_x: :class:`SchemaBase` obj with 'required*' attribs

        @return list of tuple rules.
        """
        if field_x.required_if is None:
            return []

        if not isinstance(field_x.required_if, list):
            msg = f"Can't build rule for {field_x.ref} - required_if isn't a list"
            self.log_failure(msg)
            return []

        # Rule saying that field_x doesn't have a value
        field_empty_rule = ContraintRule(
            switch_field=None,  # template renders this as `self`
            switch_method_call=f".is_empty_field('{field_x.ref}')",
            switch_value=True,
            operand="==",
        )

        field_rules = []
        for ruleset, msg in self.build_rule_block(field_x.required_if, field_x):

            # Application type check is rendered by the template in a different way so
            # shouldn't have the empty field check

            if any([isinstance(r, ApplicationTypeRule) for r in ruleset]):
                if len(ruleset) == 1:
                    # simple single rule is supported by templating
                    field_rules.append(ruleset[0])
                else:
                    # Not supported simply because it's not been needed.
                    msg = (
                        f"Unexpected specification format. {field_x.ref}'s required_if not "
                        "supported in template"
                    )
                    self.log_failure(msg)

            else:
                r_op = RuleConjunction(msg, *ruleset, field_empty_rule)
                field_rules.append(r_op)

        return field_rules

    def applies_if_rules(self, field_x):
        """
        Build rules for `out_of_scope_fields` method built by templating.

        @return: list of tuples. Tuples are either no items or two items
            First item is ApplicationTypeRule
            This is a super simple representation of a scope rule. It's simple for ease of implementing
            this template. It can be expanded on later.
        """
        if field_x.applies_if is None:
            return []

        # Not sure why `applies-if` and `required-if` have different layouts.
        # Check and complain if they don't match the expected formats.
        if not isinstance(field_x.applies_if, dict):
            msg = f"Can't build rule for {field_x.ref} - applies_if isn't a dictionary"
            self.log_failure(msg)
            return []

        field_rules = []
        for ruleset, msg in self.build_rule_block([field_x.applies_if], field_x):

            # see method doc. string. This is about simplification rather than completeness of
            # template
            app_type_rule = None
            other_rule = None

            if len(ruleset) == 0:
                continue
            elif len(ruleset) == 1 and isinstance(ruleset[0], ApplicationTypeRule):
                app_type_rule = ruleset[0]
            elif len(ruleset) == 1 and isinstance(ruleset[0], ContraintRule):
                other_rule = ScopedContraintRule(scope_field=field_x.ref, **ruleset[0]._asdict())
            elif len(ruleset) == 2:
                if isinstance(ruleset[0], ApplicationTypeRule):
                    app_type_rule = ruleset[0]
                    other_rule = ruleset[1]
                else:
                    app_type_rule = ruleset[1]
                    other_rule = ruleset[0]
            else:
                # simplistic implementation - template assumes conjunction
                msg = f"Unsupported applies if rules for {field_x.ref}. Template needs updating."
                self.log_failure(msg)
                return []

            if other_rule is not None and not isinstance(
                other_rule, (ContraintRule, ScopedContraintRule)
            ):
                # simplistic implementation
                msg = f"Unsupported applies if secondary rule for {field_x.ref}. Template needs updating."
                self.log_failure(msg)
                return []

            field_rules.append((app_type_rule, other_rule))

        return field_rules

    def build_rule_block(self, conditions_section, field_x):
        """
        Take a section from the specification and build `ContraintRule` + `ApplicationTypeRule` +
        `RuleDisjunction` + `RuleConjunction` objects that can be used by the template system.
        """
        rule_blocks = []  # ops (list), msg (str)
        for rule in conditions_section:
            if "any" in rule or "all" in rule:

                logical_op = "any" if "any" in rule else "all"
                if not isinstance(rule[logical_op], list):
                    msg = f"Can't build rule for {field_x.ref} - '{logical_op}' field isn't a list"
                    self.log_failure(msg)
                    return

                # ditch 'msg' return from :meth:`build_contraint_rule` and ignore fields that can't
                # currently be rendered (rule is None)
                equality_rules = []
                for rule in rule[logical_op]:
                    c_rule = self.build_contraint_rule(field_x.ref, rule)[0]
                    if c_rule is not None:
                        equality_rules.append(c_rule)

                deduped_fields = list(set([r.switch_field for r in equality_rules]))
                deduped_fields.sort()  # deterministic order for tests
                msg_fields = ", ".join(deduped_fields)

                if logical_op == "any":
                    msg = (
                        'f"One or more matches required for {self.node_path} in '
                        f'field(s): {msg_fields}"'
                    )
                    r_disjunct_op = RuleDisjunction(msg, *equality_rules)
                    rule_blocks.append(([r_disjunct_op], msg))

                elif logical_op == "all":
                    msg = (
                        'f"All fields need to match for {self.node_path} with '
                        f'field(s): {msg_fields}"'
                    )
                    rule_blocks.append((equality_rules, msg))

            else:
                c_rule, msg = self.build_contraint_rule(field_x.ref, rule)
                if c_rule:
                    rule_blocks.append(([c_rule], msg))

        return rule_blocks

    def build_contraint_rule(self, field_ref, rule):
        """
        @param field_ref: (str) - name of field
        @param rule: (dict) - block from specification doc. describing conditions around a field
        @return: (contraint, msg) - (ContraintRule, str)
                constaint - expected to be ANDed with empty field rule
                msg is user friendly python renderer-able string that will be used by templating
                engine to build python output
        """
        if "value" in rule:
            # 'if' rule
            v = safe_literal(rule["value"])

            r = ContraintRule(
                switch_field=rule["field"],
                switch_value=v,
                operand="==",
            )
            # will be rendered into python
            field_path = self.node_path_absolute(rule["field"])
            msg = f"f'{{self.node_path}}.{field_ref} is needed for current value in {field_path}'"
            return r, msg

        if "in" in rule:
            # member of list
            members = [safe_literal(v) for v in rule["in"]]
            m = ", ".join(members)
            v_members = f"[{m}]"
            r = ContraintRule(
                switch_field=rule["field"],
                switch_value=v_members,
                operand="in",
            )
            # will be rendered into python
            field_path = self.node_path_absolute(rule["field"])
            msg = (
                f"f'{{self.node_path}}.{field_ref} requires value from {v_members} in {field_path}'"
            )

            return r, msg

        if "operator" in rule and rule["operator"] == "not_empty":

            r = ContraintRule(
                switch_field=None,  # template renders this as `self`
                switch_method_call=f".is_empty_field('{rule['field']}')",
                switch_value=False,
                operand="==",
            )
            # will be rendered into python
            field_path = self.node_path_absolute(rule["field"])
            msg = f"f'{{self.node_path}}.{field_ref} requires non-empty value in {field_path}'"
            return r, msg

        if "operator" in rule and rule["operator"] == "empty":

            r = ContraintRule(
                switch_field=None,  # template renders this as `self`
                switch_method_call=f".is_empty_field('{rule['field']}')",
                switch_value=True,
                operand="==",
            )

            # will be rendered into python
            field_path = self.node_path_absolute(rule["field"])
            msg = f"f'{{self.node_path}}.{field_ref} requires empty value in {field_path}'"
            return r, msg

        if "operator" in rule and rule["operator"] == "<":
            msg = "Less than inequality needs to be implemented"
            self.log_failure(msg)
            return None, None

        if "contains" in rule and isinstance(rule["contains"], str):

            v = safe_literal(rule["contains"])
            v_members = f"[{v}]"
            r = ContraintRule(
                switch_field=rule["field"],
                switch_value=v_members,
                operand="in",
            )
            # will be rendered into python
            field_path = self.node_path_absolute(rule["field"])
            msg = (
                f"f'{{self.node_path}}.{field_ref} requires value from {v_members} in {field_path}'"
            )

            return r, msg

        if "contains" in rule and isinstance(rule["contains"], dict) and "in" in rule["contains"]:

            members = [safe_literal(v) for v in rule["contains"]["in"]]
            m = ", ".join(members)
            v_members = f"[{m}]"
            r = ContraintRule(
                switch_field=rule["field"],
                switch_value=v_members,
                operand="in",
            )
            # will be rendered into python
            field_path = self.node_path_absolute(rule["field"])
            msg = (
                f"f'{{self.node_path}}.{field_ref} requires value from {v_members} in {field_path}'"
            )
            return r, msg

        if (
            "application-type" in rule
            and isinstance(rule["application-type"], dict)
            and "in" in rule["application-type"]
        ):

            # see detailed explanation in constructor doc. for `application_inheritance_map`
            members = []
            for app_type in rule["application-type"]["in"]:
                # either use m or substitute in all children of m
                for app_type_resolved in self.application_inheritance_map.get(app_type, [app_type]):
                    members.append(safe_literal(app_type_resolved))

            m = ", ".join(members)
            v_members = f"{{{m}}}"
            # will be rendered into python
            field_path = self.node_path_absolute(field_ref)
            msg = f"f'{{self.node_path}}.{field_ref} is needed when application type is in [{v_members}]'"

            r = ApplicationTypeRule(
                switch_field=field_ref,
                app_type_match=v_members,
                rule_message=msg,
            )
            return r, msg

        # can't build rule - is serious as there will be a missing rule(s) in the output. In strict
        # mode will result in an exception
        msg = f"Can't build rule for {field_ref}"
        self.log_failure(msg)

        return None, None

    def node_path_absolute(self, field_name):
        """
        Macro type function to return 'python string' for use by template.

        The 'python string' allows the template to render the absolute node path to a field
        when either given a field or a field which is already an absolute path.
        """
        if "." in field_name:
            return field_name

        return f"{{self.node_path}}.{field_name}"

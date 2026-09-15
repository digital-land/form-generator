from collections import namedtuple
import warnings


from builder import safe_literal


SHOW_WARNINGS = False
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

    @classmethod
    def rules(cls, field_x):
        """
        Informal structure whilst code is taking shape to specify arguments
        for template to build validation rules based on field values elsewhere
        in the schema node tree.

        @param field_x: :class:`SchemaBase` obj with 'required*' attribs

        @return list of tuple rules.
        """
        field_rules = []

        if field_x.required_if:
            # Used to build SchemaNode.valid_node method in template

            if not isinstance(field_x.required_if, list):
                if SHOW_WARNINGS:
                    msg = f"Can't build rule for {field_x.ref} - required_if isn't a list"
                    warnings.warn(msg)

                return []

            # Rule saying that field_x doesn't have a value
            field_empty_rule = ContraintRule(
                switch_field=None,  # template renders this as `self`
                switch_method_call=f".is_empty_field('{field_x.ref}')",
                switch_value=True,
                operand="==",
            )

            for rule in field_x.required_if:
                # if bool rule

                if "value" in rule:
                    # 'if' rule
                    v = safe_literal(rule["value"])

                    r = ContraintRule(
                        switch_field=rule["field"],
                        switch_value=v,
                        operand="==",
                    )
                    # will be rendered into python
                    msg = (
                        f"f'{{self.node_path}}.{field_x.ref} is needed for current value in "
                        f"{{self.node_path}}.{rule['field']}'"
                    )
                    r_op = RuleConjunction(msg, r, field_empty_rule)
                    field_rules.append(r_op)

                elif "in" in rule:
                    # member of list
                    members = [safe_literal(v) for v in rule["in"]]
                    m = ", ".join(members)
                    v = f"[{m}]"
                    r = ContraintRule(
                        switch_field=rule["field"],
                        switch_value=v,
                        operand="in",
                    )
                    # will be rendered into python
                    msg = (
                        f"f'{{self.node_path}}.{field_x.ref} is needed for current value in "
                        f"{{self.node_path}}.{rule['field']}'"
                    )
                    r_op = RuleConjunction(msg, r, field_empty_rule)
                    field_rules.append(r_op)

                elif "operator" in rule:

                    if rule["operator"] in {"empty", "not_empty"}:

                        if rule["operator"] == "not_empty":
                            op_empty = ">"

                            required_field_empty_rule = ContraintRule(
                                switch_field=None,  # template renders this as `self`
                                switch_method_call=f".is_empty_field('{rule['field']}')",
                                switch_value=False,
                                operand="==",
                            )

                        else:
                            op_empty = "=="

                            required_field_empty_rule = ContraintRule(
                                switch_field=None,  # template renders this as `self`
                                switch_method_call=f".is_empty_field('{rule['field']}')",
                                switch_value=True,
                                operand="==",
                            )

                        # empty list or string
                        # using conjunction so the field's value works with len(), e.g. string or list

                        r_none = ContraintRule(
                            switch_field=rule["field"],
                            switch_value="None",
                            operand="is not",
                        )
                        r_len = ContraintRule(
                            switch_field=rule["field"],
                            switch_method_call=".__len__()",
                            switch_value=0,
                            operand=op_empty,
                        )

                        # will be rendered into python
                        msg = f"Field validation problem for: {rule['field']}"
                        r_op = RuleConjunction(msg, required_field_empty_rule, field_empty_rule)
                        field_rules.append(r_op)

                    else:
                        if SHOW_WARNINGS:
                            o = rule["operator"]
                            msg = f"Can't build rule for {field_x.ref} - unknown operator {o}"
                            warnings.warn(msg)
                        continue

                elif "any" in rule or "all" in rule:

                    logical_op = "any" if "any" in rule else "all"

                    equality_rules = []

                    if not isinstance(rule[logical_op], list):
                        if SHOW_WARNINGS:
                            msg = f"Can't build rule for {field_x.ref} - '{logical_op}' field isn't a list"
                            warnings.warn(msg)

                        # this continue would skip any other rules built for this field but I think
                        # that's OK as this is malformed
                        continue

                    for field_eq in rule[logical_op]:

                        if "field" in field_eq:

                            if "value" in field_eq:
                                # this 'any' rule is for a field level equality
                                v = safe_literal(field_eq["value"])
                                r = ContraintRule(
                                    switch_field=field_eq["field"],
                                    switch_value=v,
                                    operand="==",
                                )
                                equality_rules.append(r)

                            elif "contains" in field_eq:

                                v = safe_literal(field_eq["contains"])
                                v_members = f"[{v}]"
                                r = ContraintRule(
                                    switch_field=field_eq["field"],
                                    switch_value=v_members,
                                    operand="in",
                                )
                                equality_rules.append(r)

                            elif SHOW_WARNINGS:
                                msg = f"'any' rule without 'container' or 'value' for {field_x.ref}"
                                warnings.warn(msg)

                        elif SHOW_WARNINGS:
                            msg = f"Can't build rule for {field_x.ref} - unknown 'any' rule"
                            warnings.warn(msg)

                    if len(equality_rules) > 0:
                        deduped_fields = list(set([r.switch_field for r in equality_rules]))
                        # deterministic order for tests
                        deduped_fields.sort()
                        msg_fields = ", ".join(deduped_fields)

                        if logical_op == "any":
                            msg = (
                                'f"One or more matches required for {self.node_path} in '
                                f'field(s): {msg_fields}"'
                            )
                            r_disjunct_op = RuleDisjunction(msg, *equality_rules)
                            r_op = RuleConjunction(msg, r_disjunct_op, field_empty_rule)

                        elif logical_op == "all":
                            msg = f"All fields need to match for field(s): {msg_fields}"
                            r_op = RuleConjunction(msg, *equality_rules, field_empty_rule)
                        else:
                            raise ValueError("Unknown logical operation when building rules.")

                        field_rules.append(r_op)

                else:
                    if SHOW_WARNINGS:
                        warnings.warn(f"Can't build rule for {field_x.ref}")
                    continue

        return field_rules

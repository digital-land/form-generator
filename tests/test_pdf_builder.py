import unittest

from reportlab.platypus import KeepTogether, Paragraph, Table

from pdf_builder.generate_application import GenerateApplication
from schema.planning_application import fusion_cls_map
from tests.sample_schema_nodes import Animal, ContactDetail, Partnership


class TestPdfBuilder(unittest.TestCase):

    def flowables(self, schema_node_cls, node_obj=None):
        """
        @param schema_node_cls: (subclass, not instance of SchemaNode)
        @param node_obj: (SchemaNode) loaded instance for scope decisions, defaults to an empty
            instance of `schema_node_cls`
        @return: list of reportlab class used to build PDFs
        """
        # constructor doesn't touch the filesystem or schema mapping - safe without rendering
        gen = GenerateApplication(
            output_filepath="unused.pdf",
            application_ref="X",
            schema_node_map=fusion_cls_map,
        )
        flowables = gen._node_flowables(schema_node_cls, node_obj or schema_node_cls())
        return flowables

    def extract_field_block(self, schema_node_cls, label, node_obj=None):
        """
        @return: the KeepTogether field block whose first paragraph text is `label`, or None.
        """
        for f in self.flowables(schema_node_cls, node_obj=node_obj):
            if isinstance(f, KeepTogether):
                paras = [c for c in f._content if isinstance(c, Paragraph)]
                if paras and paras[0].text == label:
                    return f
        return None

    def test_string_field_has_label_and_write_box(self):
        """
        email` has no display - falls back to the attribute name, and no description
        """
        block = self.extract_field_block(ContactDetail, "email")
        self.assertIsNotNone(block)

        labels = [c.text for c in block._content if isinstance(c, Paragraph)]
        self.assertEqual(["email"], labels)

        tables = [c for c in block._content if isinstance(c, Table)]
        self.assertEqual(1, len(tables), "a string field should produce a single write box")

    def test_nested_node_rendered_as_section(self):
        """
        `fax` is a plain node field, `phones` is a RepeatedField wrapping a node - both render
        their target node as an indented section
        """
        # (list of (text, style_name)) for the top-level heading paragraphs.
        flowables = self.flowables(ContactDetail)
        headers = [(f.text, f.style.name) for f in flowables if isinstance(f, Paragraph)]

        self.assertIn(("FaxNumber", "section"), headers)
        self.assertIn(("PhoneNumber", "section"), headers)

    def test_nested_node_field_rendered_as_field_block(self):
        """
        both FaxNumber and PhoneNumber expose a `number` string field
        """
        self.assertIsNotNone(self.extract_field_block(ContactDetail, "number"))

    def test_out_of_scope_leaf_field_not_rendered(self):
        """
        A leaf field a node puts out of scope isn't rendered.
        """
        # Animal puts `location` (the `where` repeated field) out of scope for Bob
        bob = Animal()
        bob.set_payload({"keeper": {"email": "bob@thezoo.com"}})
        self.assertIsNone(self.extract_field_block(Animal, "where", node_obj=bob))

        # in scope for anyone else
        tim = Animal()
        tim.set_payload({"keeper": {"email": "tim@thezoo.com"}})
        self.assertIsNotNone(self.extract_field_block(Animal, "where", node_obj=tim))

    def test_out_of_scope_node_not_rendered(self):
        """
        A whole child node (and its descendant sections) a node puts out of scope isn't rendered.
        """

        def contact_sections(node_obj):
            # each ContactDetail node renders a section header with its class name
            return [
                f
                for f in self.flowables(Partnership, node_obj=node_obj)
                if isinstance(f, Paragraph) and f.text == "ContactDetail"
            ]

        # Partnership puts the `person-b` node out of scope for a sole trader
        sole = Partnership()
        sole.set_payload({"person-a": {"email": "sole-trader@me.com"}})
        c = contact_sections(sole)
        self.assertEqual(1, len(c))

        # both people rendered otherwise
        pair = Partnership()
        pair.set_payload({"person-a": {"email": "a@me.com"}})
        c = contact_sections(pair)
        self.assertEqual(2, len(c))

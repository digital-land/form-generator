import unittest

from reportlab.platypus import KeepTogether, Paragraph, Table

from pdf_builder.generate_application import GenerateApplication
from schema.planning_application import fusion_cls_map
from tests.sample_schema_nodes import ContactDetail


class TestPdfBuilder(unittest.TestCase):

    def flowables(self, schema_node_cls):
        """
        @param schema_node_cls: (subclass, not instance of SchemaNode)
        @return: list of reportlab class used to build PDFs
        """
        # constructor doesn't touch the filesystem or schema mapping - safe without rendering
        gen = GenerateApplication(
            output_filepath="unused.pdf",
            application_ref="X",
            schema_node_map=fusion_cls_map,
        )
        flowables = gen._node_flowables(schema_node_cls)
        return flowables

    def extract_field_block(self, schema_node_cls, label):
        """
        @return: the KeepTogether field block whose first paragraph text is `label`, or None.
        """
        for f in self.flowables(schema_node_cls):
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

        self.assertIn(("FaxNumber_FusionCls", "section"), headers)
        self.assertIn(("PhoneNumber_FusionCls", "section"), headers)

    def test_nested_node_field_rendered_as_field_block(self):
        """
        both FaxNumber and PhoneNumber expose a `number` string field
        """
        self.assertIsNotNone(self.extract_field_block(ContactDetail, "number"))

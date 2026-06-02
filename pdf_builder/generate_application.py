from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch

from schema.schema_tree import AbstractSchemaField, SchemaNodeField
from schema.planning_applications import schema_node_root_mapping

cm = 2.54
PAGE_HEIGHT = defaultPageSize[1]
PAGE_WIDTH = defaultPageSize[0]
styles = getSampleStyleSheet()


class GenerateApplication:
    def __init__(self, output_filepath, application_ref, page_size=defaultPageSize):
        """
        @param application_ref: (str) - ref from schema
        """
        self.output_filepath = output_filepath
        self.application_ref = application_ref
        self.page_size = page_size
        self.page_width = page_size[0]
        self.page_height = page_size[1]

    #
    # def _dump_fields(self, schema_node_class):
    #     """
    #     POC/demo/hello world - just get some field names
    #     """
    #
    #     schema_fields = []
    #     for attr_name, attr_value in vars(schema_node_class).items():
    #         if attr_name.startswith("_") or not isinstance(attr_value, AbstractSchemaField):
    #             continue
    #         label = attr_value.display or attr_name
    #         schema_fields.append(label)
    #
    #     return schema_fields

    def _dump_all_fields(self, schema_node_class):
        """
        POC/demo/hello world - just get some field names
        """

        schema_fields = []
        for attr_name, attr_value in vars(schema_node_class).items():
            if attr_name.startswith("_") or not isinstance(attr_value, AbstractSchemaField):
                continue

            if isinstance(attr_value, SchemaNodeField):
                schema_fields.extend(self._dump_all_fields(attr_value.schema_node_cls))
            else:
                label = attr_value.display or attr_name
                schema_fields.append(label)

        return schema_fields

    def go(self):
        """
        Build the PDF.
        """
        pageinfo = "PDF example"

        def first_page(canvas, doc):
            canvas.saveState()
            canvas.setFont("Times-Bold", 16)
            canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, self.application_ref)
            canvas.setFont("Times-Roman", 9)
            canvas.drawString(inch, 0.75 * inch, "First Page / %s" % pageinfo)
            canvas.restoreState()

        def other_pages(canvas, doc):
            canvas.saveState()
            canvas.setFont("Times-Roman", 9)
            canvas.drawString(inch, 0.75 * inch, "Page %d %s" % (doc.page, pageinfo))
            canvas.restoreState()

        doc = SimpleDocTemplate(
            self.output_filepath,
            rightMargin=0,
            leftMargin=6.5 * cm,
            topMargin=0.3 * cm,
            bottomMargin=0,
        )
        doc_elements = [Spacer(1, 2 * inch)]

        schema_node_class = schema_node_root_mapping[self.application_ref]

        data = []
        for field in self._dump_all_fields(schema_node_class):
            data.append((field, ""))

        table = Table(data, colWidths=(defaultPageSize[0] * 0.2, defaultPageSize[0] * 0.8))
        doc_elements.append(table)

        doc.build(doc_elements, onFirstPage=first_page, onLaterPages=other_pages)


if __name__ == "__main__":

    app_pdf = GenerateApplication(output_filepath="hello_application.pdf", application_ref="hh")
    app_pdf.go()

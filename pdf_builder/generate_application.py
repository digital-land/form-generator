from reportlab.lib.colors import black, grey
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from schema.planning_application import planning_application_roots_mapping
from schema.fields import (
    AbstractSchemaField,
    BooleanField,
    EnumField,
    RepeatedField,
    SchemaNodeField,
)


class GenerateApplication:
    """
    Build a printable (non-interactive) planning application form. Each field is rendered with
    its name, description and an empty area to be completed by hand.
    """

    # height of the empty box a person writes their answer into
    WRITE_BOX_HEIGHT = 1.4 * cm
    # size of the square a person ticks
    TICK_BOX_SIZE = 0.7 * cm
    # radius used to slightly round the corners of boxes and checkboxes
    BOX_CORNER_RADIUS = 0.1 * cm

    def __init__(self, output_filepath, application_ref, page_size=A4):
        """
        @param output_filepath: (str) - where to write the PDF
        @param application_ref: (str) - ref from schema
        @param page_size: (tuple) - reportlab page size
        """
        self.output_filepath = output_filepath
        self.application_ref = application_ref
        self.page_size = page_size
        self.page_width = page_size[0]
        self.page_height = page_size[1]
        self.left_margin = 2 * cm
        self.right_margin = 2 * cm
        self.content_width = self.page_width - self.left_margin - self.right_margin
        self.styles = self._build_styles()

    def _build_styles(self):
        """
        @return: (dict) named :class:`ParagraphStyle` used to render the form.
        """
        base = getSampleStyleSheet()
        return {
            "form_title": ParagraphStyle(
                "form_title", parent=base["Title"], alignment=0, spaceAfter=4
            ),
            "form_description": ParagraphStyle(
                "form_description",
                parent=base["Normal"],
                textColor=grey,
                spaceAfter=10,
            ),
            "section": ParagraphStyle(
                "section",
                parent=base["Heading2"],
                spaceBefore=14,
                spaceAfter=2,
            ),
            "section_description": ParagraphStyle(
                "section_description",
                parent=base["Normal"],
                textColor=grey,
                fontSize=9,
                spaceAfter=6,
            ),
            "field_label": ParagraphStyle(
                "field_label",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                spaceBefore=8,
                spaceAfter=2,
            ),
            "field_description": ParagraphStyle(
                "field_description",
                parent=base["Normal"],
                textColor=grey,
                fontSize=9,
                spaceAfter=4,
            ),
            "option": ParagraphStyle("option", parent=base["Normal"]),
            "note": ParagraphStyle(
                "note",
                parent=base["Normal"],
                textColor=grey,
                fontSize=8,
                spaceAfter=4,
            ),
        }

    def _write_box(self):
        """
        @return: (Table) an empty bordered box for the user to write an answer into.
        """
        box = Table([[""]], colWidths=[self.content_width], rowHeights=[self.WRITE_BOX_HEIGHT])
        box.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, black),
                    ("ROUNDEDCORNERS", [self.BOX_CORNER_RADIUS] * 4),
                ]
            )
        )
        box.hAlign = "LEFT"
        return box

    def _checkbox_row(self, text):
        """
        @return: (Table) a tick box next to `text`, used for an option to select.
        """
        tick = Table([[""]], colWidths=[self.TICK_BOX_SIZE], rowHeights=[self.TICK_BOX_SIZE])
        tick.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.75, black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROUNDEDCORNERS", [self.BOX_CORNER_RADIUS] * 4),
                ]
            )
        )

        label_width = self.content_width - self.TICK_BOX_SIZE - 0.4 * cm
        row = Table(
            [[tick, Paragraph(text, self.styles["option"])]],
            colWidths=[self.TICK_BOX_SIZE + 0.4 * cm, label_width],
        )
        row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ("LEFTPADDING", (0, 0), (0, 0), 0),
                ]
            )
        )
        row.hAlign = "LEFT"
        return row

    def _field_flowables(self, field, attr_name, repeated):
        """
        Render a single (non-node) field: its name, description and an area to complete.

        @param field: (AbstractSchemaField) - the field, already unwrapped from any RepeatedField
        @param attr_name: (str) - fallback name if the field has no display
        @param repeated: (bool) - whether multiple answers are allowed
        @return: (list of flowables)
        """
        elements = []
        label = field.display or attr_name
        elements.append(Paragraph(label, self.styles["field_label"]))

        if field.description:
            elements.append(Paragraph(field.description, self.styles["field_description"]))

        if repeated:
            elements.append(Paragraph("You may provide more than one answer.", self.styles["note"]))

        if isinstance(field, EnumField):
            for opt in field.select_options:
                opt_label = opt.label
                if opt.description:
                    opt_label += f" – {opt.description}"
                elements.append(self._checkbox_row(opt_label))
        elif isinstance(field, BooleanField):
            elements.append(self._checkbox_row("Yes"))
            elements.append(self._checkbox_row("No"))
        else:
            # StringField or anything else - a free text box
            elements.append(self._write_box())

        elements.append(Spacer(1, 0.3 * cm))
        # keep a field and its input area on the same page where possible
        return [KeepTogether(elements)]

    def _node_flowables(self, schema_node_class, field=None):
        """
        Recursively render a schema node as a section of the form.

        @param schema_node_class: (SchemaNode subclass)
        @param field: (SchemaNodeField) - the field that referenced this node, if any. Its
            display/description take precedence over the node's own. None for the root node.
        @return: (list of flowables)
        """
        elements = []
        is_root = field is None

        display = (field.display if field else None) or getattr(schema_node_class, "_display", None)
        description = (field.description if field else None) or getattr(
            schema_node_class, "_description", None
        )

        header_style = self.styles["form_title"] if is_root else self.styles["section"]
        elements.append(Paragraph(display or schema_node_class.__name__, header_style))
        if description:
            desc_style = (
                self.styles["form_description"] if is_root else self.styles["section_description"]
            )
            elements.append(Paragraph(description, desc_style))

        for attr_name, attr_value in vars(schema_node_class).items():
            if attr_name.startswith("_") or not isinstance(attr_value, AbstractSchemaField):
                continue

            repeated = isinstance(attr_value, RepeatedField)
            inner = attr_value.schema_field if repeated else attr_value

            if isinstance(inner, SchemaNodeField):
                elements.extend(self._node_flowables(inner.schema_node_cls, field=inner))
            else:
                elements.extend(self._field_flowables(inner, attr_name, repeated))

        return elements

    def _on_page(self, canvas, doc):
        """
        Footer with a page number, drawn on every page.
        """
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(grey)
        canvas.drawCentredString(self.page_width / 2.0, 1 * cm, f"Page {doc.page}")
        canvas.restoreState()

    def go(self):
        """
        Build the PDF.
        """
        doc = SimpleDocTemplate(
            self.output_filepath,
            pagesize=self.page_size,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=f"Planning application: {self.application_ref}",
        )

        schema_node_class = planning_application_roots_mapping[self.application_ref]
        elements = self._node_flowables(schema_node_class)

        doc.build(elements, onFirstPage=self._on_page, onLaterPages=self._on_page)


if __name__ == "__main__":

    app_pdf = GenerateApplication(output_filepath="hello_application.pdf", application_ref="hh")
    app_pdf.go()

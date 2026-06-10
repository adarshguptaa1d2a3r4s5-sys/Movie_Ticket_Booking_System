import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
)
from utils.price_calculator import calculate_seat_price


# ── Colour Palette ──────────────────────────────────────────────────────────
BRAND_RED      = colors.HexColor("#E50914")
DARK_BG        = colors.HexColor("#0F172A")
HEADER_BG      = colors.HexColor("#1E293B")
ROW_ALT        = colors.HexColor("#F1F5F9")
ROW_WHITE      = colors.HexColor("#FFFFFF")
TEXT_DARK       = colors.HexColor("#1E293B")
TEXT_MUTED      = colors.HexColor("#64748B")
BORDER_LIGHT   = colors.HexColor("#CBD5E1")
ACCENT_GREEN   = colors.HexColor("#16A34A")


def _styles():
    """Build all paragraph styles used across the invoice."""
    base = getSampleStyleSheet()

    return {
        "company_name": ParagraphStyle(
            "CompanyName", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=22, textColor=BRAND_RED,
            spaceAfter=2, leading=26,
        ),
        "company_tagline": ParagraphStyle(
            "CompanyTagline", parent=base["Normal"],
            fontName="Helvetica", fontSize=8, textColor=TEXT_MUTED,
            spaceAfter=0,
        ),
        "invoice_title": ParagraphStyle(
            "InvoiceTitle", parent=base["Heading1"],
            fontName="Helvetica-Bold", fontSize=26, textColor=DARK_BG,
            alignment=TA_RIGHT, spaceAfter=2,
        ),
        "invoice_meta_label": ParagraphStyle(
            "InvoiceMetaLabel", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_MUTED,
            alignment=TA_RIGHT,
        ),
        "invoice_meta_value": ParagraphStyle(
            "InvoiceMetaValue", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK,
            alignment=TA_RIGHT,
        ),
        "section_heading": ParagraphStyle(
            "SectionHeading", parent=base["Heading2"],
            fontName="Helvetica-Bold", fontSize=11, textColor=BRAND_RED,
            spaceBefore=14, spaceAfter=6,
        ),
        "label": ParagraphStyle(
            "Label", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_MUTED,
        ),
        "value": ParagraphStyle(
            "Value", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK,
            leading=13,
        ),
        "value_bold": ParagraphStyle(
            "ValueBold", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9, textColor=TEXT_DARK,
            leading=13,
        ),
        "table_header": ParagraphStyle(
            "TableHeader", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=9, textColor=colors.white,
        ),
        "table_cell": ParagraphStyle(
            "TableCell", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK,
        ),
        "table_cell_right": ParagraphStyle(
            "TableCellRight", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK,
            alignment=TA_RIGHT,
        ),
        "table_cell_center": ParagraphStyle(
            "TableCellCenter", parent=base["Normal"],
            fontName="Helvetica", fontSize=9, textColor=TEXT_DARK,
            alignment=TA_CENTER,
        ),
        "total_label": ParagraphStyle(
            "TotalLabel", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=11, textColor=TEXT_DARK,
            alignment=TA_RIGHT,
        ),
        "total_value": ParagraphStyle(
            "TotalValue", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=13, textColor=BRAND_RED,
            alignment=TA_RIGHT,
        ),
        "status_paid": ParagraphStyle(
            "StatusPaid", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=10, textColor=ACCENT_GREEN,
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "Footer", parent=base["Normal"],
            fontName="Helvetica", fontSize=7.5, textColor=TEXT_MUTED,
            leading=10,
        ),
        "footer_bold": ParagraphStyle(
            "FooterBold", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=8, textColor=TEXT_MUTED,
            spaceBefore=4, spaceAfter=2,
        ),
        "thank_you": ParagraphStyle(
            "ThankYou", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=12, textColor=BRAND_RED,
            alignment=TA_CENTER, spaceBefore=10,
        ),
    }


def generate_ticket_pdf(booking, qr_image_bytes):
    """
    Generates a professional invoice-style PDF ticket in memory and returns
    the raw bytes.

    Args:
        booking: A Booking ORM model instance with relationships populated.
        qr_image_bytes: Raw bytes of the generated QR code PNG.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=35, rightMargin=35,
        topMargin=30, bottomMargin=30,
    )
    S = _styles()
    story = []
    page_width = A4[0] - 70  # usable width after margins

    movie   = booking.show.movie
    theatre = booking.show.theatre
    show    = booking.show
    user    = booking.user

    # ════════════════════════════════════════════════════════════════════════
    # 1. HEADER  —  Brand + "INVOICE" + invoice meta
    # ════════════════════════════════════════════════════════════════════════
    brand_block = [
        [Paragraph("🎬 CineTicket", S["company_name"])],
        [Paragraph("Your Premium Movie Booking Experience", S["company_tagline"])],
    ]
    brand_table = Table(brand_block, colWidths=[page_width * 0.5])
    brand_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
    ]))

    invoice_meta = [
        [Paragraph("INVOICE", S["invoice_title"])],
        [Paragraph("Invoice No.", S["invoice_meta_label"])],
        [Paragraph(booking.booking_reference, S["invoice_meta_value"])],
        [Paragraph("Date of Issue", S["invoice_meta_label"])],
        [Paragraph(booking.booking_date.strftime("%B %d, %Y"), S["invoice_meta_value"])],
        [Paragraph("Status", S["invoice_meta_label"])],
        [Paragraph("✓ PAID", S["status_paid"])],
    ]
    meta_table = Table(invoice_meta, colWidths=[page_width * 0.5])
    meta_table.setStyle(TableStyle([
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
    ]))

    header = Table([[brand_table, meta_table]], colWidths=[page_width * 0.5, page_width * 0.5])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(header)

    # Red accent line below header
    story.append(Spacer(1, 8))
    story.append(HRFlowable(
        width="100%", thickness=2, color=BRAND_RED,
        spaceAfter=12, spaceBefore=0,
    ))

    # ════════════════════════════════════════════════════════════════════════
    # 2. BILLED TO  /  SHOW DETAILS  — two-column block
    # ════════════════════════════════════════════════════════════════════════
    def _info_pair(label, value, styles=S):
        return [Paragraph(label, styles["label"]), Paragraph(value, styles["value"])]

    billed_data = [
        [Paragraph("BILLED TO", S["section_heading"])],
        [Paragraph(user.name, S["value_bold"])],
        [Paragraph(user.email, S["value"])],
        [Paragraph(user.phone or "—", S["value"])],
    ]
    billed_table = Table(billed_data, colWidths=[page_width * 0.45])
    billed_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))

    show_details_data = [
        [Paragraph("SHOW DETAILS", S["section_heading"])],
        [Paragraph(f"{movie.title}  ({movie.language})", S["value_bold"])],
        [Paragraph(f"{movie.genre}  •  {movie.duration} mins", S["value"])],
        [Paragraph(f"{theatre.name}, {theatre.city}", S["value"])],
        [Paragraph(
            f"Screen {show.screen_number}  •  "
            f"{show.show_date.strftime('%A, %B %d, %Y')}  •  "
            f"{show.show_time.strftime('%I:%M %p')}",
            S["value"],
        )],
    ]
    show_table = Table(show_details_data, colWidths=[page_width * 0.55])
    show_table.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
    ]))

    info_row = Table([[billed_table, show_table]],
                     colWidths=[page_width * 0.45, page_width * 0.55])
    info_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(info_row)
    story.append(Spacer(1, 14))

    # ════════════════════════════════════════════════════════════════════════
    # 3. LINE ITEMS TABLE  —  itemized seat breakdown
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("ITEMISED CHARGES", S["section_heading"]))

    col_widths = [
        page_width * 0.08,   # #
        page_width * 0.22,   # Seat
        page_width * 0.25,   # Category
        page_width * 0.15,   # Qty
        page_width * 0.15,   # Unit Price
        page_width * 0.15,   # Amount
    ]

    table_data = [[
        Paragraph("#", S["table_header"]),
        Paragraph("Seat", S["table_header"]),
        Paragraph("Category", S["table_header"]),
        Paragraph("Qty", S["table_header"]),
        Paragraph("Unit Price (₹)", S["table_header"]),
        Paragraph("Amount (₹)", S["table_header"]),
    ]]

    subtotal = 0.0
    for idx, seat in enumerate(booking.seats, start=1):
        unit_price = calculate_seat_price(seat.seat_type)
        subtotal += unit_price
        table_data.append([
            Paragraph(str(idx), S["table_cell_center"]),
            Paragraph(seat.seat_number, S["table_cell"]),
            Paragraph(seat.seat_type, S["table_cell"]),
            Paragraph("1", S["table_cell_center"]),
            Paragraph(f"{unit_price:,.2f}", S["table_cell_right"]),
            Paragraph(f"{unit_price:,.2f}", S["table_cell_right"]),
        ])

    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Build row-alternating style
    ts_cmds = [
        # Header row
        ("BACKGROUND",    (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        # Grid
        ("GRID",          (0, 0), (-1, -1), 0.4, BORDER_LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [ROW_WHITE, ROW_ALT]),
        # Padding
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        # Alignment
        ("ALIGN",         (0, 0), (0, -1), "CENTER"),
        ("ALIGN",         (3, 0), (3, -1), "CENTER"),
        ("ALIGN",         (4, 0), (5, -1), "RIGHT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]
    items_table.setStyle(TableStyle(ts_cmds))
    story.append(items_table)
    story.append(Spacer(1, 6))

    # ════════════════════════════════════════════════════════════════════════
    # 4. TOTALS BLOCK  — right-aligned summary
    # ════════════════════════════════════════════════════════════════════════
    gst             = round(subtotal * 0.18, 2)
    convenience_fee = 30.0
    grand_total     = round(subtotal + gst + convenience_fee, 2)

    summary_label_w = page_width * 0.35
    summary_value_w = page_width * 0.20
    # Push totals to the right with a spacer column
    spacer_w = page_width - summary_label_w - summary_value_w

    summary_data = [
        ["", Paragraph("Subtotal", S["value"]),
         Paragraph(f"₹ {subtotal:,.2f}", S["table_cell_right"])],
        ["", Paragraph("GST (18%)", S["value"]),
         Paragraph(f"₹ {gst:,.2f}", S["table_cell_right"])],
        ["", Paragraph("Convenience Fee", S["value"]),
         Paragraph(f"₹ {convenience_fee:,.2f}", S["table_cell_right"])],
        ["", Paragraph("GRAND TOTAL", S["total_label"]),
         Paragraph(f"₹ {grand_total:,.2f}", S["total_value"])],
    ]
    summary_table = Table(summary_data, colWidths=[spacer_w, summary_label_w, summary_value_w])
    summary_table.setStyle(TableStyle([
        ("LINEABOVE",    (1, 0), (-1, 0), 0.5, BORDER_LIGHT),
        ("LINEABOVE",    (1, 3), (-1, 3), 1.2, DARK_BG),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LEFTPADDING",  (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ("ALIGN",        (-1, 0), (-1, -1), "RIGHT"),
        # Highlight total row
        ("BACKGROUND",   (1, 3), (-1, 3), ROW_ALT),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    # ════════════════════════════════════════════════════════════════════════
    # 5. QR CODE + ADMISSION NOTE
    # ════════════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceAfter=10))

    qr_io  = io.BytesIO(qr_image_bytes)
    qr_img = Image(qr_io, width=1.4 * inch, height=1.4 * inch)

    qr_note_data = [
        [Paragraph("SCAN FOR ENTRY", S["section_heading"])],
        [Paragraph(
            "Present this QR code at the theatre entrance for contactless entry. "
            "A printed or digital copy is accepted.",
            S["value"],
        )],
        [Paragraph(f"Ref: {booking.booking_reference}", S["label"])],
    ]
    qr_note_table = Table(qr_note_data, colWidths=[page_width * 0.6])
    qr_note_table.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
    ]))

    qr_row = Table([[qr_img, qr_note_table]],
                   colWidths=[1.6 * inch, page_width - 1.6 * inch])
    qr_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",  (0, 0), (0, 0), "CENTER"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(qr_row)
    story.append(Spacer(1, 14))

    # ════════════════════════════════════════════════════════════════════════
    # 6. TERMS & CONDITIONS
    # ════════════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_LIGHT, spaceAfter=6))
    story.append(Paragraph("TERMS &amp; CONDITIONS", S["footer_bold"]))

    terms = [
        "1. Carry a printed or digital copy of this invoice with the QR code for entry.",
        "2. Tickets once booked cannot be exchanged or refunded unless cancellation protection was purchased.",
        "3. Outside food and beverages are not allowed inside the theatre.",
        "4. Standard age-rating restrictions apply. Please carry valid photo ID for 'A' rated movies.",
        "5. The management reserves the right of admission.",
        "6. Please arrive at least 15 minutes before the show start time.",
    ]
    for t in terms:
        story.append(Paragraph(t, S["footer"]))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 7. FOOTER
    # ════════════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_RED, spaceAfter=6))
    story.append(Paragraph(
        "Thank you for choosing CineTicket — Enjoy your movie! 🍿",
        S["thank_you"],
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This is a computer-generated invoice and does not require a physical signature.",
        ParagraphStyle("Disclaimer", parent=S["footer"], alignment=TA_CENTER),
    ))

    # ── Build ────────────────────────────────────────────────────────────
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

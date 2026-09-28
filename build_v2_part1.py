"""Build project_v2.docx — Retail Store Management System, black-only theme.
Merges front page.docx (Certificate/Declaration/Ack text preserved, title updated
per user vote) + content.docx chapter structure rewritten with REAL store numbers.
"""
import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

OUT = "project_v2.docx"
BLACK = RGBColor(0, 0, 0)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

TITLE = "Retail Store Management System"

# ---------- helpers ----------
def fix(s: str) -> str:
    if not s:
        return s
    s = s.replace("\uFFFD", "")
    s = s.replace("�", "")
    s = s.replace("—", "-").replace("–", "-")
    # normalise quotes to straight for safety in code contexts only; keep prose quotes simple
    s = re.sub(r"[\u2018\u2019]", "'", s)
    s = re.sub(r"[\u201C\u201D]", '"', s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def set_cell_shading(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    tcPr.append(shd)

def set_table_header_black(table):
    for cell in table.rows[0].cells:
        set_cell_shading(cell, "000000")
        for p in cell.paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.color.rgb = WHITE
                r.font.bold = True
                r.font.size = Pt(11)
                r.font.name = "Times New Roman"
    # repeat header + no row split
    tbl = table._tbl
    tblPr = tbl.tblPr if tbl.tblPr is not None else OxmlElement("w:tblPr")
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        cant.set(qn("w:val"), "true")
        trPr.append(cant)
    first_trPr = table.rows[0]._tr.get_or_add_trPr()
    hdr = OxmlElement("w:tblHeader")
    hdr.set(qn("w:val"), "true")
    first_trPr.append(hdr)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

def add_page_number_footer(doc):
    sec = doc.sections[0]
    sec.footer.is_linked_to_previous = False
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.text = ""
    r = fp.add_run()
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    r._r.append(fld1); r2 = fp.add_run(); r2._r.append(instr); r3 = fp.add_run(); r3._r.append(fld2)
    for run in fp.runs:
        run.font.name = "Times New Roman"; run.font.size = Pt(10); run.font.color.rgb = BLACK

def h1(doc, text, page_break=True):
    if page_break:
        doc.add_page_break()
    p = doc.add_heading(level=1)
    r = p.add_run(text)
    r.font.color.rgb = BLACK; r.font.size = Pt(16); r.font.bold = True
    r.font.name = "Times New Roman"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    pf.space_after = Pt(6); pf.space_before = Pt(12); pf.keep_with_next = True
    return p

def h2(doc, text):
    p = doc.add_heading(level=2)
    r = p.add_run(text)
    r.font.color.rgb = BLACK; r.font.size = Pt(13); r.font.bold = True
    r.font.name = "Times New Roman"
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.space_before = Pt(6)
    return p

def body(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(fix(text))
    r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.color.rgb = BLACK
    pf = p.paragraph_format
    pf.line_spacing = 1.5; pf.space_after = Pt(6); pf.space_before = Pt(0)
    return p

def bullets(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        # clear default run and add styled
        p.text = ""
        r = p.add_run(fix(it))
        r.font.name = "Times New Roman"; r.font.size = Pt(12); r.font.color.rgb = BLACK
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.5

def code_block(doc, text):
    for chunk in text.strip("\n").split("\n"):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        pf = p.paragraph_format
        r = p.add_run(chunk if chunk else " ")
        r.font.name = "Consolas"; r.font.size = Pt(8.5)
    # spacer after block
    s = doc.add_paragraph(); s.paragraph_format.space_after = Pt(6)
    s.add_run("").font.size = Pt(4)

def caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(fix(text))
    r.italic = True; r.font.size = Pt(11); r.font.name = "Times New Roman"
    r.font.color.rgb = BLACK
    p.paragraph_format.space_after = Pt(12)
    return p

def figure(doc, img_path, caption_text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(img_path, width=Inches(5.5))
    # center handled by paragraph alignment
    caption(doc, caption_text)

def make_table(doc, headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for j, htxt in enumerate(headers):
        c = t.rows[0].cells[j]
        c.text = ""
        pr = c.paragraphs[0]; pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rn = pr.add_run(fix(htxt)); rn.bold = True
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = t.rows[i].cells[j]
            c.text = ""
            pr = c.paragraphs[0]
            rn = pr.add_run(fix(str(val)))
            rn.font.name = "Times New Roman"; rn.font.size = Pt(11)
    set_table_header_black(t)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t

# ---------- document ----------
doc = docx.Document()
# base Normal
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"; normal.font.size = Pt(12); normal.font.color.rgb = BLACK
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
for st in ("Heading 1", "Heading 2", "Heading 3", "Title"):
    if st in doc.styles:
        doc.styles[st].font.color.rgb = BLACK
        doc.styles[st].font.name = "Times New Roman"
doc.styles["Heading 1"].font.size = Pt(16); doc.styles["Heading 1"].font.bold = True
doc.styles["Heading 2"].font.size = Pt(13); doc.styles["Heading 2"].font.bold = True

# ===== p1 COVER =====
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("SCHOOL OF COMPUTING"); r.bold = True; r.font.size = Pt(14)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Department of Data Science"); r.font.size = Pt(12)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Cornerstone Project Report"); r.bold = True; r.font.size = Pt(16)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run(TITLE); r.bold = True; r.font.size = Pt(18)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.add_run("B.Tech. Data Science - Academic Year 2026-2027").font.size = Pt(12)
body(doc, "A complete Oracle database for a medium-sized retail store covering products, categories, suppliers, customers and billing, with auto-calculated bill totals via a PL/SQL trigger and formatted SQL*Plus receipts, plus a Flask POS web application over the same six-table design.")
make_table(doc, ["Student", "Roll No"],
           [["N. VARALAKSHMI", "25B11CS669"],
            ["A. NITYA SRI", "25B11CS012"],
            ["S. UDAYA SATYA", "25B11CS851"],
            ["M. VIJAYA PARDHU", "26B21CS058"]])
body(doc, "Project Guide: Dr. M V B Murali Krishna, Department of Data Science. Head of the Department: Dr. M. Rajababu, Ph.D, Associate Professor, Department of Data Science.")

# ===== p2 CERTIFICATE (text preserved from front page.docx, title updated) =====
h1(doc, "CERTIFICATE")
body(doc, "This is to certify that the Cornerstone project work entitled \"Retail Store Management System\" is submitted by N. Varalakshmi (25B11CS669), A. Nitya Sri (25B11CS012), S. Udaya Satya (25B11CS851) and M. Vijaya Pardhu (26B21CS058) in partial fulfillment of the requirements for the award of the B.Tech. degree in Data Science for the academic year 2026-2027.")
body(doc, "Project Guide: Dr. M V B Murali Krishna, Department of Data Science. Head of the Department: Dr. M. Rajababu, Ph.D, Associate Professor, Department of Data Science.")

# ===== p3 DECLARATION + ACKNOWLEDGEMENT =====
h1(doc, "DECLARATION")
body(doc, "We hereby declare that the Cornerstone project entitled \"Retail Store Management System\" is original and is submitted to ADITYA UNIVERSITY, Surampalem, in partial fulfillment of the requirements for the award of the B.Tech. Degree in Data Science. We further declare that this project work has not been submitted, either in full or in part, for the award of any degree in this or any other institution. We also confirm that this work complies with the Institutional Academic Integrity and AI Usage Policy. Place: Surampalem. Date: ________.")
body(doc, "By: N. Varalakshmi (25B11CS669), A. Nitya Sri (25B11CS012), S. Udaya Satya (25B11CS851), M. Vijaya Pardhu (26B21CS058).")
h1(doc, "ACKNOWLEDGEMENT", page_break=False)
body(doc, "It is with immense pleasure that we express our sincere gratitude to our Cornerstone Project Guide, Dr. M V B Murali Krishna, who has guided us throughout the project. His valuable support, encouragement, and guidance have greatly contributed to the successful completion of this work.")
body(doc, "We would like to thank our Deputy Heads of the Department, Dr. Chandra Sekhar Kolli, Associate Professor and Deputy HOD-1, Dr. Hari Jyothula, Associate Professor and Deputy HOD-2, Dr. Pennada Siva Satya Prasad, Assistant Professor and Deputy HOD-3, Department of CSE, for their support and valuable suggestions.")
body(doc, "Our deepest thanks to our Head of the Department, Dr. Phani Sridhar Addepalli, Assistant Professor and HOD, for her inspiration and for providing all the necessary facilities and resources required for this project.")
body(doc, "We also extend our sincere thanks to Dr. M.V. Rajesh, Associate Dean, School of Computing, for his encouragement and support during our project.")
body(doc, "We would like to express our sincere gratitude to Dr. G. Suresh, Registrar; Dr. A. Ramesh, Pro Vice-Chancellor (Engineering and Sciences); Dr. S. Rama Sree, Pro Vice-Chancellor (Academics); Dr. M.B. Srinivas, Vice-Chancellor; and Dr. M. Sreenivasa Reddy, Deputy Pro Chancellor and Management, Aditya University, for providing excellent infrastructure and state-of-the-art laboratories.")
body(doc, "Finally, we would like to thank the faculty members, lab technicians, non-teaching staff, and our friends who have directly or indirectly supported us in completing this Cornerstone project successfully.")

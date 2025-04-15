from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def write_feedback_to_docx(submission_path: str, feedback_text: str, output_path: str):
    doc = Document(submission_path)

    # Split feedback into inline and summary
    if "Summary Feedback:" in feedback_text:
        inline_text, summary_text = feedback_text.split("Summary Feedback:", 1)
    else:
        inline_text = feedback_text
        summary_text = ""

    inline_lines = [line.strip() for line in inline_text.split("\n") if line.strip().startswith("-")]

    # Create a new document for output
    output_doc = Document()

    # Add original paragraphs with feedback injected
    for para in doc.paragraphs:
        p = output_doc.add_paragraph()
        added = False
        for line in inline_lines:
            if line.startswith("- \"") and "\" -" in line:
                quoted, comment = line.split("\" -", 1)
                quoted = quoted[3:]  # remove leading - "
                comment = comment.strip()

                if quoted in para.text:
                    before, match, after = para.text.partition(quoted)

                    p.add_run(before)
                    match_run = p.add_run(match)
                    match_run.bold = True

                    feedback_run = p.add_run(f" [{comment}]")
                    feedback_run.italic = True

                    p.add_run(after)
                    added = True
                    break

        if not added:
            p.add_run(para.text)

    # Add a horizontal rule then summary
    output_doc.add_paragraph("\n")
    summary_header = output_doc.add_paragraph("Summary Feedback:")
    summary_header.runs[0].bold = True

    for line in summary_text.strip().split("\n"):
        if line:
            output_doc.add_paragraph(line.strip())

    output_doc.save(output_path)

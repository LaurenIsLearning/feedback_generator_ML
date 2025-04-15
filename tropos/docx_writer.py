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

    # Parse inline feedback lines
    inline_lines = [line.strip() for line in inline_text.split("\n") if line.strip().startswith("- ")]
    
    # Extract quote-comment pairs from lines starting with '- "quoted text"' format
    feedback_pairs = []
    for line in inline_lines:
        if '"' in line:
            try:
                quoted = line.split('"')[1]
                comment = line.split('"')[2].strip(" -–—:")  # trims various dashes and colons
                feedback_pairs.append((quoted.strip(), comment.strip()))
            except IndexError:
                continue

    # Inject feedback into paragraphs
    for para in doc.paragraphs:
        for quoted, comment in feedback_pairs:
            if quoted in para.text:
                # Split the paragraph where the quote appears
                parts = para.text.split(quoted)
                if len(parts) >= 2:
                    para.clear()
                    para.add_run(parts[0])
                    bold_run = para.add_run(quoted)
                    bold_run.bold = True
                    italic_run = para.add_run(f" [{comment}]")
                    italic_run.italic = True
                    para.add_run(parts[1])
                break

    # Add summary section
    doc.add_paragraph("")  # spacing
    summary_header = doc.add_paragraph("Summary Feedback:")
    summary_header.runs[0].bold = True

    for line in summary_text.strip().split("\n"):
        if line.strip():
            doc.add_paragraph(line.strip())

    doc.save(output_path)
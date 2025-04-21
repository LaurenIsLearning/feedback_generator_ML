from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from tropos.preprocess_docx import StudentSubmission


def write_feedback_to_docx(submission_path: str, feedback_text: str, output_path: str, target: StudentSubmission):
    doc = Document(submission_path)

    #default fallbacks
    inline_text = feedback_text
    summary_text = ""
    rubric_text = ""

    # Split using exact section markers (created in prompt_builder.py)
    if "--- RUBRIC FEEDBACK ---" in feedback_text:
        inline_summary_part, rubric_text = feedback_text.split("--- RUBRIC FEEDBACK ---", 1)
    else:
        inline_summary_part = feedback_text

    if "--- SUMMARY FEEDBACK ---" in inline_summary_part:
        inline_text, summary_text = inline_summary_part.split("--- SUMMARY FEEDBACK ---", 1)
    else:
        inline_text = inline_summary_part

    #extract inline feedback pairs
    inline_lines = [line.strip() for line in inline_text.split("\n") if line.strip().startswith("- ")]
    feedback_pairs = []
    for line in inline_lines:
        if '"' in line:
            try:
                quoted = line.split('"')[1]
                comment = line.split('"')[2].strip(" -–—:")  # trims various dashes and colons
                feedback_pairs.append((quoted.strip(), comment.strip()))
            except IndexError:
                continue

    # inject inline feedback
    for para in doc.paragraphs:
        for quoted, comment in feedback_pairs:
            if quoted in para.text:
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

    # add feedback summary section
    if summary_text.strip():
        doc.add_paragraph("")
        header = doc.add_paragraph("Summary Feedback:")
        header.runs[0].bold = True
        for line in summary_text.strip().split("\n"):
            if line.strip():
                doc.add_paragraph(line.strip())

    # add rubric TABLE with feedback section
    if rubric_text.strip() and hasattr(target, "rubric"):
        doc.add_paragraph("")
        header = doc.add_paragraph("Rubric Feedback:")
        header.runs[0].bold = True

        # Step 1: Parse model rubric feedback as dict
        rubric_feedback_map = {}
        for line in rubric_text.strip().split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                rubric_feedback_map[key.strip()] = val.strip()

        # Step 2: Generate rubric table
        rubric = target.rubric  # assume this is passed in as part of StudentSubmission
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Project Portion"
        hdr_cells[1].text = "Ideal Criteria"
        hdr_cells[2].text = "Overall Feedback"

        for portion in rubric.get_criteria():
            portion_name = portion["portion"]
            criteria_text = "\n• " + "\n• ".join(c["text"] for c in portion["criteria"])
            feedback = rubric_feedback_map.get(portion_name, "[No feedback provided]")

            row_cells = table.add_row().cells
            row_cells[0].text = portion_name
            row_cells[1].text = criteria_text
            row_cells[2].text = feedback



    doc.save(output_path)


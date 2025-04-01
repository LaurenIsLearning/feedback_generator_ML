from spire.doc import *
from spire.doc.common import *

# --------------------------
# Rubric Data Class
# --------------------------
class Rubric:
    def __init__(self):
        self.criteria = []  # List of full rubric rows (each as a dictionary)
        self.comments = []  # Just the freeform feedback text (optional)

    def set_criteria(self, criteria):
        self.criteria = criteria
        return self

    def get_criteria(self):
        return self.criteria

    def set_comments(self, comments):
        self.comments = comments
        return self

    def get_comments(self):
        return self.comments

# --------------------------
# Extracts highlighted text from a cell (ideal criteria column)
# --------------------------
def get_highlighted_texts(cell):
    highlights = []

    # Loop through paragraphs in the table cell
    for para in cell.Paragraphs:
        # Loop through child objects (text ranges) inside the paragraph
        for obj in para.ChildObjects:
            if hasattr(obj, "CharacterFormat"):
                color = obj.CharacterFormat.HighlightColor

                # Only include text with a highlight (not "NoColor")
                if color != TextHighlightColor.NoColor:
                    highlights.append({
                        "text": obj.Text.strip(),
                        "highlight": str(color)  # Converts enum to readable string
                    })
    return highlights

# --------------------------
# Main rubric parser function
# --------------------------
def parse_rubric(submission: Document) -> "Rubric":
    rubric = Rubric()

    # Get all tables in the document and assume the rubric is the last one
    tables = submission.Sections[0].Tables
    rubric_table = tables[-1]

    rubric_data = []     # List to hold full parsed rows
    feedback_only = []   # Optional: just overall feedback text

    # Grab header row to locate column indices by name
    header_row = rubric_table.Rows[0]
    headers = [cell.Paragraphs[0].Text.strip() for cell in header_row.Cells]

    # Try to find the column indices by header name
    try:
        idx_portion = headers.index("Project Portion")
        idx_criteria = headers.index("Ideal Criteria")
        idx_feedback = headers.index("Overall Feedback")
    except ValueError as e:
        print("Rubric column headers not found:", e)
        return rubric

    # Go through each subsequent row in the rubric
    for row in rubric_table.Rows[1:]:
        cells = row.Cells

        # Extract text from "Project Portion" column
        portion = "\n".join([p.Text.strip() for p in cells[idx_portion].Paragraphs])

        # Extract text and highlights from "Ideal Criteria" column
        criteria_cell = cells[idx_criteria]
        criteria_text = "\n".join([p.Text.strip() for p in criteria_cell.Paragraphs])
        highlights = get_highlighted_texts(criteria_cell)

        # Extract text from "Overall Feedback" column
        feedback = "\n".join([p.Text.strip() for p in cells[idx_feedback].Paragraphs])

        # Store this entire row in a structured format
        rubric_data.append({
            "portion": portion,
            "criteria": {
                "text": criteria_text,
                "highlights": highlights
            },
            "feedback": feedback
        })

        feedback_only.append(feedback)  # For quick access later if needed

    # Attach the parsed info to the Rubric object
    rubric.set_criteria(rubric_data)
    rubric.set_comments(feedback_only)

    return rubric

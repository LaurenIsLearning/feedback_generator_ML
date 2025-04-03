from docx import Document

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
# TODO: implement later
# --------------------------


# --------------------------
# Main rubric parser function
# --------------------------
def parse_rubric(doc_path: str) -> "Rubric":
    rubric = Rubric()
    doc = Document(doc_path)

    # Assume last table is rubric
    if not doc.tables:
      print("No tables in document.")
      return rubric

    table = doc.tables[-1]

    # parse header row
    header_cells = table.rows[0].cells
    headers = [cell.text.strip() for cell in header_cells]

    try:
      # Try to find the column indices by header name
      idx_portion = headers.index("Project Portion")
      idx_criteria = headers.index("Ideal Criteria")
      idx_feedback = headers.index("Overall Feedback")
    except ValueError as e:
      print("Expected rubric column headers not found:", e)
      return rubric

    criteria_data = []
    comments = []

    # Go through each subsequent row in the rubric
    for row in table.rows[1:]:
      cells = row.cells
      
      portion = cells[idx_portion].text.strip()
      criteria_text = cells[idx_criteria].text.strip()
      feedback = cells[idx_feedback].text.strip()

      # Store this entire row in a structured format
      criteria_data.append({
        "portion": portion,
        "criteria": {
        "text": criteria_text,
        # TODO: "highlights": highlights
        },
        "feedback": feedback
      })

      comments.append(feedback)  # For quick access later if needed

    # Attach the parsed info to the Rubric object
    rubric.set_criteria(criteria_data)
    rubric.set_comments(comments)

    return rubric
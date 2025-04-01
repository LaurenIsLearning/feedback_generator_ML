from re import T
import zipfile
import xml.etree.ElementTree as ET
from docx import Document
# accessed Raw XML to get highlight colors

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
# Extracts highlighted text from .docx (reads document.xml directly)
# --------------------------
def extract_highlighted_phrases(docx_path):
  # opens .docx like a zip archive
  with zipfile.ZipFile(docx_path) as docx_zip:
    with docx_zip.open("word/document.xml") as document_xml:
      tree = ET.parse(document_xml)
      root = tree.getroot()

  #define the WordprocessingML namespace
  namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
  highlighted_phrases = []

  #loop through all <w:r> (text runs) in doc
  # extract highlight and attached text
  for run in root.findall(".//w:r", namespaces):
    rpr = run.find("w:rPr", namespaces)
    text_elem = run.find(".//w:t", namespaces)

    #if both present, store
    if rpr is not None and text_elem is not None:
      highlight = rpr.find("w:highlight", namespaces)
      if highlight is not None:
        color = highlight.attrib.get(f"{{{namespaces['w']}}}val")
        text = text_elem.text
        if text and color:
          highlighted_phrases.append({
            "text": text.strip(),
            "highlight": color
          })
  return highlighted_phrases


# --------------------------
# Main rubric parser function
# --------------------------
def parse_rubric(docx_path: str) -> "Rubric":
    rubric = Rubric()
    doc = Document(docx_path)

    if not doc.tables:
      print("No tables in document.")
      return rubric

    # assuming last table is rubric
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

    highlights = extract_highlighted_phrases(docx_path)
    criteria_data = []
    comments = []

    # Go through each subsequent row in the rubric
    for row in table.rows[1:]:
      cells = row.cells
      
      portion = cells[idx_portion].text.strip()
      criteria_text = cells[idx_criteria].text.strip()
      feedback = cells[idx_feedback].text.strip()

      #match highlights that appear in criteria cell
      matched_highlights = highlights

      # Store this entire row in a structured format
      criteria_data.append({
        "portion": portion,
        "criteria": {
        "text": criteria_text,
        "highlights": matched_highlights
        },
        "feedback": feedback
      })

      comments.append(feedback)  # For quick access later if needed

    # Attach the parsed info to the Rubric object
    rubric.set_criteria(criteria_data)
    rubric.set_comments(comments)

    return rubric

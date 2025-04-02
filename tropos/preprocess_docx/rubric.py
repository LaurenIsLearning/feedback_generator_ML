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
        self.baseline = []  # full rubric without instructor input
        self.commented = [] # instructor interventions (highlight+comments)

    def set_baseline(self, baseline):
        self.baseline = baseline
        return self

    def get_baseline(self):
        return self.baseline

    def set_commented(self, commented):
        self.commented = commented
        return self

    def get_commented(self):
        return self.commented

# --------------------------
# Extracts highlighted text from document.xml
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

    all_highlights = extract_highlighted_phrases(docx_path)
    baseline = {}
    parsed_rows = []

    # Go through each subsequent row in the rubric
    for row in table.rows[1:]:
      cells = row.cells
      
      portion = cells[idx_portion].text.strip()
      criteria_text = cells[idx_criteria].text.strip()
      feedback = cells[idx_feedback].text.strip()

      #split criteria into bullet points/lines
      criteria_lines = [line.strip() for line in criteria_text.split("\n") if line.strip()]
      baseline[portion] = criteria_lines

      # only match highlights that appear in this specific criteria cell
      cell_highlights = [h for h in all_highlights if h["text"] in criteria_text]

      #match highlights that appear in criteria cell
      matched_criteria = []
      for line in criteria_lines:
        match = next((h for h in cell_highlights if h["text"] in line), None)
        matched_criteria.append({
          "text": line,
          "highlighted": match is not None,
          "highlight": match["highlight"] if match else None
        })

      parsed_rows.append({
        "portion": portion,
        "criteria": matched_criteria,
        "overall_feedback": feedback
      })

    # Attach the parsed info to the Rubric object
    rubric.set_baseline(baseline)
    rubric.set_commented(parsed_rows)

    return rubric

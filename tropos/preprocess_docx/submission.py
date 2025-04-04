from docx import Document
from docx.opc.exceptions import PackageNotFoundError

class Submission:
    def __init__(self):
        self._content = ""
        self.metadata = {}

    def set_content(self, content):
        self._content = content
        return self
    
    def get_content(self):
        return self._content

class SubmissionProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.rubric_keywords = ["rubric", "grading", "score"]

    def process(self):
        sub = Submission()
        try:
            doc = Document(self.file_path)
            content = "\n".join(
                para.text for para in doc.paragraphs
                if self._valid_paragraph(para)
            )
            return sub.set_content(content)
        except PackageNotFoundError:
            return sub.set_content("Invalid document")
        except Exception as e:
            return sub.set_content(f"Error: {str(e)}")

    def _valid_paragraph(self, para):
        text = para.text.strip().lower()
        return text and not any(kw in text for kw in self.rubric_keywords)

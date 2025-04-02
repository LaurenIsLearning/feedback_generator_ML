from docx import Document
from docx.opc.exceptions import PackageNotFoundError

class StudentTextExtractor:
    def __init__(self, file_path, is_assignment=False):
        """
        Initializes the text extractor for either assignments or student submissions.
        :param file_path: Path to the .docx file
        :param is_assignment: True for assignment templates, False for student submissions (default)
        """
        self.file_path = file_path
        self.is_assignment = is_assignment
        self.rubric_keywords = ["rubric", "grading", "score", "criteria", "assessment"]

    def extract_text(self):
        """
        Main extraction method that safely retrieves content.
        :return: Extracted text or error message
        """
        try:
            doc = Document(self.file_path)
            return self._process_document(doc)
        except PackageNotFoundError:
            return "Error: Invalid or corrupted .docx file"
        except Exception as e:
            return f"Error: {str(e)}"

    def _process_document(self, doc):
        """Routes to appropriate extraction method based on document type"""
        if self.is_assignment:
            return self._extract_instructions(doc)
        return self._extract_student_content(doc)

    def _extract_instructions(self, doc):
        """Extracts only assignment instructions (excludes rubrics/metadata)"""
        return "\n".join(
            para.text for para in doc.paragraphs
            if self._is_valid_instruction(para)
        )

    def _extract_student_content(self, doc):
        """Extracts only student-written body text (excludes rubrics/templates)"""
        content = "\n".join(
            para.text for para in doc.paragraphs
            if self._is_valid_student_text(para)
        )
        return self._remove_rubric_tables(doc, content)

    def _is_valid_instruction(self, para):
        """Validates paragraphs for assignment instructions"""
        text = para.text.strip()
        return (bool(text) and 
               not any(kw in text.lower() for kw in self.rubric_keywords) and
               para.style.name.lower() not in ["title", "header", "footer"])

    def _is_valid_student_text(self, para):
        """Validates paragraphs for student-written content"""
        text = para.text.strip()
        return (bool(text) and 
               not any(kw in text.lower() for kw in self.rubric_keywords) and
               para.style.name.lower() not in ["title", "heading 1", "heading 2", "instruction"])

    def _remove_rubric_tables(self, doc, content):
        """Excludes any tables containing rubric-related content"""
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if any(kw in cell.text.lower() for kw in self.rubric_keywords):
                        return content  # Return original content if rubric table found
        return content
    
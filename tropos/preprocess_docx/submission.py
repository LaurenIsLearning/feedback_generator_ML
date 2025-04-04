from docx import Document

class Submission:
    def __init__(self):
        self._content = ""
        self.metadata = {}

    def set_content(self, content):
        self._content = content
        return self
    
    def get_content(self):
        return self._content

def parse_submission(submission: Document) -> Submission:
    sub = Submission()
    try:
        content = []
        for para in submission.paragraphs:
            text = para.text.strip()
            if text and not any(kw in text.lower() for kw in ["rubric", "grading", "score"]):
                content.append(text)
        sub.set_content("\n".join(content))
    except Exception as e:
        sub.set_content(f"Error: {str(e)}")
    return sub

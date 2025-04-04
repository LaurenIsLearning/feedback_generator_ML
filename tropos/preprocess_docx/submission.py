from docx import Document 

class Submission:
    def __init__(self):
        self._content = ""

    def set_content(self, content):
        self._content = content
        return self
    
    def get_content(self):
        return self._content

def parse_submission(submission: Document) -> Submission:  # Now uses python-docx Document
    """Preserves original logic with python-docx syntax"""
    sub = Submission()
    try:
        content = []
        # Python-docx equivalent of Spire's text extraction
        for para in submission.paragraphs:
            text = para.text.strip()
            if text:
                content.append(text)
        sub.set_content("\n".join(content))
    except Exception as e:
        sub.set_content(f"Error: {str(e)}")
    return sub

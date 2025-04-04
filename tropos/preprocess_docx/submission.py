from docx import Document  

class AssignmentRequirements:
    def __init__(self):
        self._instructions = ""

    def set_instructions(self, text):
        self._instructions = text
        return self
    
    def get_instructions(self):
        return self._instructions

def parse_requirements(doc_path: str) -> AssignmentRequirements: 
    """Original logic adapted for python-docx"""
    req = AssignmentRequirements()
    try:
        doc = Document(doc_path)  # python-docx loading
        instructions = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                instructions.append(text)
        req.set_instructions("\n".join(instructions))
        
    except Exception as e:
        req.set_instructions(f"Error: {str(e)}")
    return req

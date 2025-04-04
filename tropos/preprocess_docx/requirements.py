from docx import Document
from .text_extractor import AssignmentTextExtractor

class Requirements:
    def __init__(self):
        self._instructions = ""
        self.metadata = {}

    def set_instructions(self, text):
        self._instructions = text
        return self
    
    def get_instructions(self):
        return self._instructions

def parse_requirements(doc_path: str) -> Requirements:
    """Mirrors your submission.py structure"""
    req = Requirements()
    try:
        extractor = AssignmentTextExtractor(doc_path)
        instructions = extractor.extract_instructions()
        return req.set_instructions(instructions)
    except Exception as e:
        return req.set_instructions(f"Error: {str(e)}")

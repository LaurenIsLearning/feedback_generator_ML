from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

class Submission:
    def __init__(self):
        self._content = ""

    def set_content(self, content):
        self._content = content
        return self
    
    def get_content(self):
        return self._content

def iter_block_items(doc):
    """
    Yield paragraphs and tables in document order.
    """
    parent = doc.element.body
    for child in parent.iterchildren():
        if child.tag.endswith("}p"):
            yield Paragraph(child, doc)
        elif child.tag.endswith("}tbl"):
            yield Table(child, doc)

def parse_submission(doc: Document) -> Submission:
    """Extracts all paragraph text before the final table (rubric)."""
    sub = Submission()
    try:
        content = []
        blocks = list(iter_block_items(doc))
        
        # Find the index of the last table (rubric)
        last_table_index = max(
            (i for i, block in enumerate(blocks) if isinstance(block, Table)),
            default=len(blocks)
        )

        # Collect paragraph text before the last table
        for block in blocks[:last_table_index]:
            if isinstance(block, Paragraph):
                text = block.text.strip()
                if text:
                    content.append(text)

        sub.set_content("\n".join(content))
        
    except Exception as e:
        sub.set_content(f"Error: {str(e)}")
    
    return sub

from typing import TypedDict
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import parse_xml
from docx.oxml.ns import qn
import zipfile
from typing import List


class CommentInfo(TypedDict):
    """
    All of the info related to a comment
    """

    comment_id: str
    comment_text: str
    commented_text: str
    paragraph: str
    author: str
    data: str


class Comments:

    results: List[CommentInfo]

    def __init__(self, doc_path):
        self.doc_path = doc_path
        self.doc = Document(doc_path)
        self.comments = []
        self.comment_refs = {}
        self.results = []

    def parse_comments(self):
        """Main method to extract all comments and their context"""
        self._extract_comment_content()
        self._find_comment_references()
        # Compiles information based on the comments and their references
        self.results = [
            {
                "comment_id": c["id"],
                "comment_text": c["text"],
                "commented_text": self.comment_refs.get(c["id"], {}).get("text", ""),
                "paragraph": self.comment_refs.get(c["id"], {}).get("paragraph", ""),
                "author": c["author"],
                "date": c["date"],
            }
            for c in self.comments
        ]
        return self

    def _extract_comment_content(self):
      """Extract comment content from the docx archive"""
      try:
          with zipfile.ZipFile(self.doc_path) as z:
              # Look for any comments XML file (comments.xml, comments1.xml, etc.)
              comment_file = next((f for f in z.namelist()
                                   if f.startswith("word/comments") and f.endswith(".xml")), None)
              if not comment_file:
              #DEBUG (commented out bc there is files without comments and dont want that to look like an error.)
              #    print(f"⚠️ No comments file found in {self.doc_path}")
                  return
  
              with z.open(comment_file) as f:
                  comments_xml = parse_xml(f.read())
                  namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
  
                  for comment in comments_xml.xpath('//w:comment', namespaces=namespace):
                      self.comments.append({
                          'id': comment.get(qn('w:id')),
                          'author': comment.get(qn('w:author'), 'Unknown'),
                          'date': comment.get(qn('w:date'), ''),
                          'text': ''.join([
                              node.text for node in 
                              comment.xpath('.//w:t', namespaces=namespace) 
                              if node.text
                          ]).strip()
                      })
  
          if not self.comments:
              print(f"⚠️ No comments extracted from {self.doc_path}")
  
      except Exception as e:
          print(f"❌ Error reading comments from {self.doc_path}: {e}")


    def _find_comment_references(self):
        """Find comment references in document text"""
        for paragraph in self.doc.paragraphs:
            for run in paragraph.runs:
                if hasattr(run, "_element"):
                    if comment_refs := run._element.xpath(".//w:commentReference"):
                        comment_id = comment_refs[0].get(qn("w:id"))
                        self.comment_refs[comment_id] = {
                            "text": run.text.strip(),
                            "paragraph": paragraph.text.strip(),
                        }

    def get_results(
        self,
    ) -> List[CommentInfo]:
        """Return structured comment data"""
        return [{
            'comment_id': c['id'],
            'comment_text': c['text'],
           #DEBUG, ADDING FOLLOWING LINE
           # 'commented_text': self.comment_refs.get(c['id'], {}).get('text') or self.comment_refs.get(c['id'], {}).get('paragraph', ''),
            'commented_text': self.comment_refs.get(c['id'], {}).get('text', ''),
            'paragraph': self.comment_refs.get(c['id'], {}).get('paragraph', ''),
            'author': c['author'],
            'date': c['date']
        } for c in self.comments]

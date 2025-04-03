from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import parse_xml
from docx.oxml.ns import qn
import zipfile

class CommentExtractor:
    def __init__(self, doc_path):
        self.doc_path = doc_path
        self.doc = Document(doc_path)
        self.comments = []
        self.comment_refs = {}

    def extract_comments(self):
        """Main method to extract all comments and their context"""
        self._extract_comment_content()
        self._find_comment_references()
        return self

    def _extract_comment_content(self):
        """Extract comment content from the docx archive"""
        try:
            with zipfile.ZipFile(self.doc_path) as z:
                with z.open('word/comments.xml') as f:
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
        except KeyError:
            print("Document contains no comments")
        except Exception as e:
            print(f"Error reading comments: {e}")

    def _find_comment_references(self):
        """Find comment references in document text"""
        for paragraph in self.doc.paragraphs:
            for run in paragraph.runs:
                if hasattr(run, '_element'):
                    if comment_refs := run._element.xpath('.//w:commentReference'):
                        comment_id = comment_refs[0].get(qn('w:id'))
                        self.comment_refs[comment_id] = {
                            'text': run.text.strip(),
                            'paragraph': paragraph.text.strip()
                        }

    def get_results(self):
        """Return structured comment data"""
        return [{
            'comment_id': c['id'],
            'comment_text': c['text'],
            'commented_text': self.comment_refs.get(c['id'], {}).get('text', ''),
            'paragraph': self.comment_refs.get(c['id'], {}).get('paragraph', ''),
            'author': c['author'],
            'date': c['date']
        } for c in self.comments]

# Add this if you want a simple function interface
def extract_comments(doc_path):
    return CommentExtractor(doc_path).extract_comments().get_results()


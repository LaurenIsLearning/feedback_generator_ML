from spire.doc import *
from spire.doc.common import *


class Rubric:

    def __init__(self):
        self.criteria = []  # List of criteria descriptions
        self.scores = []    # Corresponding possible scores or weights
        self.comments = []  # General comments or instructions

    def set_criteria(self, criteria):
        self.criteria = criteria
        return self

    def get_criteria(self):
        return self.criteria

    def set_scores(self, scores):
        self.scores = scores
        return self

    def get_scores(self):
        return self.scores

    def set_comments(self, comments):
        self.comments = comments
        return self

    def get_comments(self):
        return self.comments


    def parse_rubric(submission: Document) -> "Rubric":
        rubric = Rubric()
        # Logic to parse the rubric from the document
        # This will depend on the structure of the document
        # For example, you might look for specific tables or sections
        # and extract the relevant information
        return rubric

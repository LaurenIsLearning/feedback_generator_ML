# main function to test local/notebook setup
import os
from typing import List


class MarkdownFeedbackPrinter:
    document_name: str
    """
    The name of the current document with the file extension 
    """

    document_parts: List[str]
    """
    A new line separated list 
    """

    n_paragraphs: int
    """
    Used to track the number of paragraphs as more are added 
    """

    def __init__(self, document_name: str) -> None:
        self.document_parts = [f"# {document_name}"]
        self.n_paragraphs = 0

    def add_feedback(self, author: str, paragraph: str, feedback: str):
        self.n_paragraphs += 1
        print(f"Paragraph {self.n_paragraphs} ---\n{paragraph}")
        print("Section Feedback ---")
        print(feedback)
        self.document_parts.append(paragraph)
        self.document_parts.append(f"\n> **{author}**:\n>")
        self.document_parts.append("\n> ".join(feedback.split("\n")))

    def add_text(self, text: str):
        self.document_parts.append(text)

    def __str__(self) -> str:
        return "\n\n".join(self.document_parts)

    def write_md(self, path: str):
        with open(path, "w") as f:
            f.write(self.__str__())


__all__ = ["MarkdownFeedbackPrinter"]

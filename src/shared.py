import json


# Define InputFields and OutputFields classes
class InputFields:
    def __init__(self):
        self._student_id = None
        self._assignment_id = None
        self._requirements_input = None
        self._student_essay = None

    # getters
    def get_student_id(self):
        return self._student_id

    def get_assignment_id(self):
        return self._assignment_id

    def get_requirements_input(self):
        return self._requirements_input

    def get_student_essay(self):
        return self._student_essay

    # setters
    def set_student_id(self, value):
        self._student_id = value

    def set_assignment_id(self, value):
        self._assignment_id = value

    def set_requirements_input(self, value):
        self._requirements_input = value

    def set_student_essay(self, value):
        self._student_essay = value

    # Adder methods (builder method)
    def add_student_id(self, value):
        self._student_id = value
        return self

    def add_assignment_id(self, value):
        self._assignment_id = value
        return self

    def add_requirements_input(self, value):
        self._requirements_input = value
        return self

    def add_student_essay(self, value):
        self._student_essay = value
        return self

    # JSON parsing and serialization
    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        obj = InputFields()
        obj.set_student_id(data.get("StudentID"))
        obj.set_assignment_id(data.get("AssignmentID"))
        obj.set_requirements_input(data.get("Requirements Input"))
        obj.set_student_essay(data.get("Student Essay"))
        return obj

    def to_json(self):
        return json.dumps(
            {
                "StudentID": self._student_id,
                "AssignmentID": self._assignment_id,
                "Requirements Input": self._requirements_input,
                "Student Essay": self._student_essay,
            },
            indent=4,
        )


class OutputFields:
    def __init__(self):
        self._student_id = None
        self._assignment_id = None
        self._text_snippet = None
        self._feedback = None
        self._feedback_type = None

    # Getters
    def get_student_id(self):
        return self._student_id

    def get_assignment_id(self):
        return self._assignment_id

    def get_text_snippet(self):
        return self._text_snippet

    def get_feedback(self):
        return self._feedback

    def get_feedback_type(self):
        return self._feedback_type

    # Setters
    def set_student_id(self, value):
        self._student_id = value

    def set_assignment_id(self, value):
        self._assignment_id = value

    def set_text_snippet(self, value):
        self._text_snippet = value

    def set_feedback(self, value):
        self._feedback = value

    def set_feedback_type(self, value):
        self._feedback_type = value

    # Builder methods (adders)
    def add_student_id(self, value):
        self._student_id = value
        return self

    def add_assignment_id(self, value):
        self._assignment_id = value
        return self

    def add_text_snippet(self, value):
        self._text_snippet = value
        return self

    def add_feedback(self, value):
        self._feedback = value
        return self

    def add_feedback_type(self, value):
        self._feedback_type = value
        return self

    # JSON parsing and serialization
    @staticmethod
    def from_json(json_str):
        data = json.loads(json_str)
        obj = OutputFields()
        obj.set_student_id(data.get("Student ID"))
        obj.set_assignment_id(data.get("Assignment ID"))
        obj.set_text_snippet(data.get("Text Snippet"))
        obj.set_feedback(data.get("Feedback"))
        obj.set_feedback_type(data.get("FeedbackType"))
        return obj

    def to_json(self):
        return json.dumps(
            {
                "Student ID": self._student_id,
                "Assignment ID": self._assignment_id,
                "Text Snippet": self._text_snippet,
                "Feedback": self._feedback,
                "FeedbackType": self._feedback_type,
            }
        )

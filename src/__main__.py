import pickle


class Span:
    start: int
    end: int

    def __init__(self, start: int, end: int) -> None:
        self.start = start
        self.end = end


class FeedbackEntry:
    """
    text_span: [start_index, end_index] - what section of text that is being commented on and where it is in the text
    text_source_location:Filepath/URL - The file/text reference where the span is from
    feedback:String - The feedback based on the evaluation context and the span
    evaluation_context:Filepath/String - The context in how to evaluate the given work, like the subject and requirements.
    revision_progress: float - normalized between 0 and 1 of what revision step this paper is in
    """

    text_span: Span
    """
    The section of the text that the feedback is applied too
    """

    text_source_path: str
    """
    The file path for the text 
    """

    feedback: str
    """
    The feedback based on the given evaluation context 
    """

    # TODO: Should this be given a class rather than it just being a string
    evaluation_context: str
    """
    The context that the feedback was based on, like rubric requirements, the context and such other way to evaluate the given text.
    """

    revision_progress: float
    """
    A normalized float that shows the current document revision normalized based on the total number of revisions for the assignment 
    """

    # TODO: Finish the init, setters, getters, and pickle

class EmptyQuizAttemptedException(Exception):
    message = "This quiz does not have any question sets and cannot be attempted"

class EmptyQuestionSetException(Exception):
    message = "The question set is empty"
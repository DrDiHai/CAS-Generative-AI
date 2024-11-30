from enum import Enum

# Enum with the different types of answers that a question can have
class AnswerType(Enum):
    CLEAVAGE = 'cleavage'
    ANSWER = 'answer'
    COMMENT = 'comment'
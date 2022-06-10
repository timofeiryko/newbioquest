"""Custom classes and functions for domain logic (aka business logic).
Most of this logic is related with objects, data stuctures etc.
The `scripts.py` is the other place where domain logic is placed (just some tools, not related with particular abstractions at all)."""

from dataclasses import dataclass, field, InitVar
from email.policy import default
from typing import Type, Tuple, Dict
from collections import namedtuple


from .models import Question
from .scripts import counter_p2, points_from_matrix
from .configs import ANSWER_STYLES, EVALUATE_THRASHHOLD, P2_VAR_SET, PROGRESSIVE_SCALES

class QuestionService(Question):
    pass

@dataclass
class Compare:
    right_answer: str
    user_answer: str
    is_right: bool


@dataclass
class AnswersCheckerInterface:
    user_points: int
    max_points: int
    compare_matrix: Tuple[Compare, ...]
    user_default_score: float
    user_score: float


# Dataclass is used just to get free good representation
# Also we can create something similar to OOP interface with it
@dataclass
class AnswersChecker(AnswersCheckerInterface):
    """To check user answers.
    Methods `_set...` are used in `__post_init__` to process different type of questions."""

    raw_contents: InitVar[str]
    question: Type[Question]
    
    inputfields: Dict[str, str]= field(default_factory=dict)
    style: str = field(init=False)

    def _set_p1(self):

            right_answer = self.question.answer
            user_answer = self.raw_contents.strip()
            is_right = self.user_answer == self.right_answer
            self.compare_matrix = Compare(right_answer, user_answer, is_right)

            self.user_points, self.max_points = points_from_matrix(self.compare_matrix)
            self.user_default_score = self.question.max_score
            self.user_score = self.question.max_score


    def _set_p2(self):

        question = self.question
        if question.flag == 'CORE':
            questions_block = tuple(
                question.year,
                question.stage,
                question.grade,
                question.part
            )
        else:
            questions_block = 'DEFAULT'

        scale = PROGRESSIVE_SCALES[questions_block]
        right_answer = self.question.answer
        user_answer = self.raw_contents.strip()
        self.compare_matrix, self.user_default_score, self.user_score = counter_p2(
            right_answer, user_answer, self.question.max_score, scale, P2_VAR_SET
        )


    def __post_init__(self):

        self.style = self.question.style

        if self.style not in ANSWER_STYLES:
            raise ValueError(f'There is no "{self.style}" type of answer. Possible values are: {ANSWER_STYLES.keys()}')
        
        if self.style == 'P1':
            self._set_p1()

        if self.style == 'P2':
            pass

        if self.user_points > self.max_points:
            raise ValueError(f'Invalid data: user_points {self.user_points} > max_points {self.max_points}, it is impossible.')
        # We call it to check are all attrs initialized
        # It's a hack to do somtehing similar to OOP interfaces
        self.__repr__()

    def check(self):
        return AnswersCheckerInterface(self.user_points, self.max_points, self.user_score, self.compare_matrix)

    def evaluate_message(self) -> Tuple[str, str]:
        if self.user_points == self.max_points:
            message = 'Верно'
            status = 'right'
        elif self.user_points / self.max_points > EVALUATE_THRASHHOLD:
            message = 'Частично верно. Есть куда стремится :)'
            status = 'partial'
        else:
            message = 'Совсем мало правильных ответов :( Ботайте, и всё обязательно получится!'
            status = 'wrong'
        return message, status
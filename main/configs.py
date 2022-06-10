"""Different configs, mostly domain-specific. Used in `services.py` and `scripts.py`"""

from collections import namedtuple

ANSWER_STYLES = {
    'P1': '1 правильный ответ',
    'P2': 'Множественный выбор',
    'REL': 'Вопрос на соответствие',
    'STR': 'Текстовый ответ'
}

# Minimum ratio of right answers to say that the answer is partially correct
EVALUATE_THRASHHOLD = 0.2

P2_VAR_SET = 'абвгд'

PROGRESSIVE_SCALES = {
    'DEFAULT': (0, 0.5, 1, 1.5, 2, 2.5)
}
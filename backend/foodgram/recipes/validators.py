import re

from django.core.exceptions import ValidationError


def validate_username(username):
    invalid_chars = set(re.findall(r'[^\w.@+-]', username))
    if invalid_chars:
        raise ValidationError(
            f'Недопустимые символы в никнейме: {invalid_chars}'
        )


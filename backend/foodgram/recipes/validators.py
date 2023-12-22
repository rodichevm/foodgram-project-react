import re

from django.core.exceptions import ValidationError


def validate_username(username):
    pattern = r'^[\w.@+-]+$'
    if not re.match(pattern, username):
        invalid_chars = [char for char in username if
                         not re.match(r'[\w.@+-]', char)]
        message = (
            f'Недопустимые символы: {", ".join(invalid_chars)}'
        )
        raise ValidationError(message, code='invalid_username')

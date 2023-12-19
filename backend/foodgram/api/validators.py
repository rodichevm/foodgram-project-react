from django.core.validators import RegexValidator


class UsernameValidator(RegexValidator):
    regex = r'^[\w.@+-]+$'
    message = (
        'Никнейм может содержать буквы, числа, и следующие символы: '
        '@ . + - _'
    )
    code = 'invalid_username'

import datetime

from django.http import FileResponse


def send_message(ingredients):
    header = (
        f'Дата: {datetime.date.today().isoformat()}\n'

    )
    cart = '\n'.join(
        (
            f'{index + 1}.'
            f'{ingredient["ingredient__name"].capitalize()}'
            f' - {ingredient["amount"]}'
            f' {ingredient["ingredient__measurement_unit"]}'

            for index, ingredient in enumerate(ingredients)))

    full_message = f'{header}\nПРОДУКТЫ:\n{cart}'

    response = FileResponse(
        full_message,
        content_type='text/plain',
        filename=f'shopping_cart_{datetime.date.today().isoformat()}.txt'
    )
    return response

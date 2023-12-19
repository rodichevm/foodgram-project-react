import datetime

from django.http import FileResponse

from recipes.models import Recipe


def send_message(ingredients):
    shopping_cart = (
            f'Дата: {datetime.date.today().isoformat()}\n'
            f'ПРОДУКТЫ:\n' +
            '\n'.join(
                (f'{index + 1}. {ingredient["ingredient__name"].capitalize()}'
                 f' - {ingredient["amount"]}'
                 f' {ingredient["ingredient__measurement_unit"]}'

                 for index, ingredient in enumerate(ingredients)))
    )

    full_message = f'{shopping_cart}\n\nРЕЦЕПТЫ:'

    response = FileResponse(
        full_message,
        content_type='text/plain',
        filename=f'shopping_cart_{datetime.date.today().isoformat()}.txt'
    )
    return response

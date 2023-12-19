import datetime

from django.http import FileResponse


def send_message(ingredients):
    shopping_cart = '\n'.join(
        f'Дата: {datetime.date.today().isoformat()}'
        f'ПРОДУКТЫ:'
        f'{index + 1}. {ingredient["ingredient__name"].capitalize()} '
        f'({ingredient["ingredient__measurement_unit"]}) - '
        f'{ingredient["amount"]}'
        for index, ingredient in enumerate(ingredients))

    response = FileResponse(
        shopping_cart,
        content_type='text/plain',
        filename=f'shopping_cart_{datetime.date.today().isoformat()}.txt'
    )
    return response

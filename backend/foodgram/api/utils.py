import datetime

from django.http import FileResponse


def send_message(ingredients):
    shopping_cart = f'Дата: {datetime.date.today().isoformat()}'
    shopping_cart += '\n'.join(
        f'\n - {ingredient["ingredient__name"]})'
        f'({ingredient["ingredient__measurement_unit"]}) - '
        f'{ingredient["amount"]}'
        for ingredient in ingredients)

    file = f'shopping_cart_{datetime.date.today().isoformat()}.txt'
    response = FileResponse(shopping_cart, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={file}.txt'
    return response

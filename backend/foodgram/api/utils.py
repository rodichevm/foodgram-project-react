import datetime


def generate_shopping_cart_message(shopping_cart_list):
    result_lines = [
        f'Дата: {datetime.date.today().isoformat()}',
        '',
        'ПРОДУКТЫ:',
        *[
            f'{index + 1}.'
            f'{item["ingredient__name"].capitalize()}'
            f' - {item["amount"]}'
            f' {item["ingredient__measurement_unit"]}'
            for index, item in enumerate(shopping_cart_list)
        ],
        '',
        'РЕЦЕПТЫ:',
    ]
    for index, item in enumerate(
            set(item["recipe__name"] for item in shopping_cart_list)
    ):
        result_lines.append(
            f'{index + 1}.'
            f'{item.capitalize()}'
        )
    return '\n'.join(result_lines)

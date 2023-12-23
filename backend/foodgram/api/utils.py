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
    added_recipes = set()
    for index, item in enumerate(shopping_cart_list):
        if item["recipe__name"] not in added_recipes:
            result_lines.append(
                f'{index + 1}.'
                f'{item["recipe__name"].capitalize()}'
            )
            added_recipes.add(item["recipe__name"])

    return '\n'.join(result_lines)

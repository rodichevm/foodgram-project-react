import datetime


def send_message(data):
    result_lines = [
        f'Дата: {datetime.date.today().isoformat()}\n',
        'ПРОДУКТЫ:',
        *[
            f'{index + 1}.'
            f'{ingredient["ingredient__name"].capitalize()}'
            f' - {ingredient["amount"]}'
            f' {ingredient["ingredient__measurement_unit"]}'
            for index, ingredient in enumerate(data)
        ],
        'РЕЦЕПТЫ:',
    ]
    added_recipes = set()
    for index, recipe in enumerate(data):
        if recipe["recipe__name"] not in added_recipes:
            result_lines.append(
                f'{index + 1}.'
                f'{recipe["recipe__name"].capitalize()}'
            )
            added_recipes.add(recipe["recipe__name"])

    return '\n'.join(result_lines)

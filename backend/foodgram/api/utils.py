import datetime


def generate_shopping_cart_message(shopping_cart_list):
    ingredient_counts = {}
    for item in shopping_cart_list:
        ingredient_key = (
            item["ingredient__name"], item["ingredient__measurement_unit"]
        )
        ingredient_counts[ingredient_key] = ingredient_counts.get(
            ingredient_key, 0) + item["amount"]
    return '\n'.join(
        [
            f'Дата: {datetime.date.today().isoformat()}',
            '',
            'ПРОДУКТЫ:',
            *[
                f'{index + 1}.'
                f'{amount}'
                f' {measurement_unit}'
                f' - {name.capitalize()}'
                for index, ((name, measurement_unit), amount) in enumerate(
                    ingredient_counts.items()
                )
            ],
            '',
            'РЕЦЕПТЫ:',
            *[
                f'{index + 1}.'
                f'{item.capitalize()}'
                for index, item in enumerate(
                    set(item["recipe__name"] for item in shopping_cart_list)
                )
            ],
        ]
    )

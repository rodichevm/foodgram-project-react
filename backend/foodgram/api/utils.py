import datetime
from django.db.models import Sum

from recipes.models import IngredientAmount


def generate_shopping_cart_message(shopping_cart_list):
    ingredient_names = set(
        item['ingredient__name'] for item in shopping_cart_list)
    ingredient_amounts = (
        IngredientAmount.objects
        .filter(ingredient__name__in=ingredient_names)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(total_sum=Sum('amount'))
    )
    ingredients = {
        (item["ingredient__name"],
         item["ingredient__measurement_unit"]): item['total_sum']
        for item in ingredient_amounts
    }
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
                    ingredients.items()
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

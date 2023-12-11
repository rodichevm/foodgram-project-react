import json
import os

from django.core.management import BaseCommand
from foodgram.settings import BASE_DIR

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
                os.path.join(BASE_DIR, 'data/ingredients.json'),
                encoding='utf-8'
        ) as ingredients_file:
            data = json.loads(ingredients_file.read())
            for ingredient in data:
                Ingredient.objects.get_or_create(**ingredient)

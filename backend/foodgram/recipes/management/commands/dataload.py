import json
import os

from django.core.management import BaseCommand
from foodgram.settings import BASE_DIR

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
                os.path.join(BASE_DIR, 'data/ingredients.json'),
                encoding='utf-8'
        ) as ingredients_file:
            data = json.loads(ingredients_file.read())
            for ingredient in data:
                Ingredient.objects.get_or_create(**ingredient)
        with open(
                os.path.join(BASE_DIR, 'data/tags.json'),
                encoding='utf-8'
        ) as tags_file:
            data = json.loads(tags_file.read())
            for tag in data:
                Tag.objects.get_or_create(**tag)

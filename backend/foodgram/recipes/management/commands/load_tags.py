import json
import os

from django.core.management import BaseCommand
from foodgram.settings import BASE_DIR

from recipes.models import Tag


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(
                os.path.join(BASE_DIR, 'data/tags.json'),
                encoding='utf-8'
        ) as tags_file:
            data = json.loads(tags_file.read())
            Tag.objects.bulk_create(
                    (Tag(**tag) for tag in data),
                    ignore_conflicts=True
            )

        self.stdout.write(self.style.SUCCESS('Теги успешно импортированы'))

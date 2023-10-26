from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    color = models.CharField(
        max_length=7, verbose_name='Цвет в HEX', null=True)
    slug = models.CharField(
        max_length=200,
        null=True,
        verbose_name='Уникальный слаг',
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единицы измерения')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    tags = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Список тегов')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Список ингредиентов'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(verbose_name='Ссылка на картинку на сайте')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinValueValidator(1)]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт',
        verbose_name_plural = 'Рецепты'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, verbose_name='Рецепт ингредиента', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент из рецепта',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество', validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиенты для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'


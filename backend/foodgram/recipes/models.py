from colorfield.fields import ColorField
from distlib.util import cached_property
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from django.db.models import F, Q, UniqueConstraint
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class User(AbstractUser):

    email = models.EmailField(unique=True, verbose_name='Email')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ("username", "first_name", "last_name",)

    username = models.CharField(
        verbose_name='Никнейм',
        max_length=150,
        unique=True,
        validators=(UnicodeUsernameValidator(),)
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ('username',)

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('user',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        db_index=True
    )
    color = ColorField(
        format='hex',
        verbose_name='HEX код',
        max_length=7,
        validators=[
            RegexValidator(
                regex="^#([A-Fa-f0-9]{6})$",
                message='Неправильный формат HEX кода',
            )
        ]
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def display_color(self):
        return format_html(
            '<span style="width:20px;height:20px;display:block;background'
            '-color:{}"></span>',
            self.color)
    display_color.short_description = 'Цвет'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_name_measurement_unit'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Продукты'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/image/'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1, message='Время приготовления не менее 1 минуты'),
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.name

    @cached_property
    def display_image(self):
        html = '<img src="{img}" width="100" height="100">'
        return format_html(html, img=self.image.url)

    display_image.short_description = 'Изображение'


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredientinrecipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Продукт',
        on_delete=models.CASCADE,
        related_name='ingredientinrecipes'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('recipe', )
        verbose_name = 'Продукт для рецепта'
        verbose_name_plural = 'Продукты для рецепта'

    def __str__(self):
        return (f'{self.ingredient.name}, {self.ingredient.measurement_unit}'
                f' - {self.amount}')


class FavoriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        default_related_name = '%(class)ss'
        abstract = True
        constraints = [
            UniqueConstraint(
                fields=('user', 'recipe'),
                name='%(class)s_unique'
            )
        ]

    def __str__(self):
        return f'{self.user} : {self.recipe}'


class Favorite(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(FavoriteShoppingCart):

    class Meta(FavoriteShoppingCart.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag, User)


class CookingTimeFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    LOOKUP_VALUES = {
        'fast': {'cooking_time__lte': 15},
        'medium': {'cooking_time__gt': 15, 'cooking_time__lte': 60},
        'slow': {'cooking_time__gt': 60},
    }

    def lookups(self, request, model_admin):
        return [
            ('fast', 'Быстрые (до 15 минут)'),
            ('medium', 'Средние (15-60 минут)'),
            ('slow', 'Долгие (больше 60 минут)'),
        ]

    def queryset(self, request, recipes):
        if not self.value() or self.value() not in self.LOOKUP_VALUES:
            return recipes

        return recipes.distinct().filter(**self.LOOKUP_VALUES[self.value()])


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email',
        'get_recipes',
        'get_following',
        'get_followers',
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'

    @admin.display(description='Количество рецептов')
    def get_recipes(self, user):
        return user.recipes.count()

    @admin.display(description='Подписки')
    def get_following(self, user):
        return user.following.count()

    @admin.display(description='Подписчики')
    def get_followers(self, user):
        return user.follower.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ('id', 'user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'display_color', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'

    @admin.display(description='Цвет HEX')
    def display_color(self, obj):
        return mark_safe(
            '<div style="background-color: {}; width: 30px; height: '
            '30px;"></div>'.format(
                obj.color)
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = IngredientAmount
    extra = 3
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_display = (
        'author',
        'name',
        'cooking_time',
        'get_tags',
        'get_ingredients',
        'get_favorites',
        'get_image'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('tags__name', CookingTimeFilter, )
    inlines = (IngredientInline, )

    @admin.display(description='В избранном')
    def get_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        tags = recipe.tags.all()
        return mark_safe('<br>'.join(str(tag) for tag in tags))

    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(str(ingredient)
                        for ingredient in recipe.ingredientinrecipes.all())
        )

    @admin.display(description='Изображение')
    def get_image(self, recipe):
        return mark_safe(f'<img src={recipe.image.url} width="80" hieght="30"')

    get_ingredients.allow_tags = True


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    model = Favorite
    list_display = ('user', 'recipe')
    search_fields = list_display
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = '-пусто-'


admin.site.unregister(Group)

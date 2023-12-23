from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Min, Max
from django.utils.safestring import mark_safe

from recipes.models import (
    Favorite, Follow, Ingredient, IngredientAmount,
    Recipe, ShoppingCart, Tag, User
)


class CookingTimeFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        lookup_choices = []
        thresholds = [0, 15, 45, 10**10]

        for i in range(len(thresholds) - 1):
            low, high = thresholds[i], thresholds[i + 1]
            if low in range(0, 15):
                label = 'Быстрые'
            elif low in range(15, 45):
                label = 'Средние'
            elif low in range(45, 10**10):
                label = 'Долгие'
            else:
                label = 'Неизвестно'

            recipe_count = model_admin.get_queryset(request).filter(
                cooking_time__range=(low, high)).count()

            lookup_choices.append(
                (f'{low + 1}-{high}', f'{label} ({recipe_count} рецептов)'))

        return lookup_choices

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            low, high = map(int, value.split('-'))
            return queryset.filter(cooking_time__range=(low, high))


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = (
        'id',
        'get_name',
        'username',
        'email',
        'get_recipes',
        'get_following',
        'get_followers',
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'

    @admin.display(description='Имя')
    def get_name(self, user):
        return f'{user.first_name} {user.last_name}'

    @admin.display(description='Рецептов')
    def get_recipes(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок')
    def get_following(self, user):
        return user.follower.count()

    @admin.display(description='Подписчиков')
    def get_followers(self, user):
        return user.following.count()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ('id', 'user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'display_color', 'hex_code', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-пусто-'

    @mark_safe
    @admin.display(description='Цвет HEX')
    def display_color(self, tag):
        return (
            f'<div style="background-color: {tag.color}; width: '
            f'30px; height: 30px;"></div>'
        )

    @admin.display(description='код HEX')
    def hex_code(self, obj):
        return obj.color


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
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
    list_filter = ('tags__name', CookingTimeFilter,)
    inlines = (IngredientInline,)

    @admin.display(description='В избранном')
    def get_favorites(self, recipe):
        return recipe.favorites.count()

    @mark_safe
    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return (
            '<br>'.join(str(tag) for tag in recipe.tags.all())
        )

    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return mark_safe(
            '<br>'.join(str(ingredient)
                        for ingredient in recipe.ingredientinrecipes.all())
        )

    @admin.display(description='Изображение')
    def get_image(self, recipe):
        return mark_safe(f'<img src={recipe.image.url} width="80" hieght="30"')


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
    search_fields = ('user',)
    empty_value_display = '-пусто-'


admin.site.unregister(Group)

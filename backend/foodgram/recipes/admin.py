from django.contrib import admin
from django.contrib.admin import display
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from api.filters import CookingTimeFilter
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag, User)


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
        'has_followers'
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'

    def get_recipes(self, user):
        return user.recipes.count()

    def get_following(self, user):
        return user.following.count()

    def get_followers(self, user):
        return user.follower.count()

    def has_followers(self, user):
        return user.follower.exists()

    get_recipes.short_description = 'Количество рецептов'
    get_following.short_description = 'Подписки'
    get_followers.short_description = 'Подписчики'
    has_followers.boolean = True


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ('id', 'user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'display_color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )
    empty_value_display = '-пусто-'

    @display(description="Colored")
    def display_color(self, obj: Tag):
        return format_html(
            '<span style="color: #{};">{}</span>', obj.color[1:], obj.color
        )

    display_color.short_description = "Цвет тэга"


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
        'get_ingredients',
        'get_favorites',
        'get_image'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('tags__name', CookingTimeFilter, )
    inlines = (IngredientInline, )

    def get_favorites(self, recipe):
        return recipe.favorites.count()

    def get_ingredients(self, recipe):
        to_return = '<ul>'
        to_return += '\n'.join(
            '<li>{}</li>'.format(ingredient)
            for ingredient in recipe.ingredientinrecipes.all())
        to_return += '</ul>'
        return mark_safe(to_return)

    def get_image(self, recipe):
        return mark_safe(f'<img src={recipe.image.url} width="80" hieght="30"')

    get_ingredients.allow_tags = True
    get_favorites.short_description = 'В избранном'
    get_ingredients.short_description = 'Продукты'
    get_image.short_description = 'Изображение'


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

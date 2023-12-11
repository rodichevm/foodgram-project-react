from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


class IngredientInline(admin.TabularInline):
    model = IngredientInRecipe
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
        'get_favorites'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = search_fields
    inlines = (IngredientInline, )
    empty_value_display = '-пусто-'

    def get_favorites(self, obj):
        return obj.favorites.count()

    def get_ingredients(self, obj):
        return ', '.join([
            ingredients.name for ingredients in obj.ingredients.all()
        ])


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    model = Favorite
    list_display = ('user', 'recipe')
    list_filter = list_display
    search_fields = list_display
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('recipe', 'user')
    list_filter = list_display
    search_fields = ('user', )
    empty_value_display = '-пусто-'

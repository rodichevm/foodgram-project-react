from django.contrib import admin

from recipes.models import Recipe, Tag, Ingredient, IngredientInRecipe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'color', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')


class IngredientInRecipeAdmin(admin.TabularInline):
    model = IngredientInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_display = ('id',
                    'tags',
                    'author',
                    'name',
                    'image',
                    'text',
                    'cooking_time'
                    )
    inlines = (IngredientInRecipeAdmin, )


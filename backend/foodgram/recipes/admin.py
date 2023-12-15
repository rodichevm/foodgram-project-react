from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from recipes.models import (Favorite, Follow, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag, User)


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
    # list_filter = ()
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


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ('id', 'user', 'author')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'color', 'display_color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    model = Ingredient
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('measurement_unit', )
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
        'get_favorites',
        'display_image'
    )
    search_fields = ('name', 'author', 'tags')
    list_filter = ('tags', )
    inlines = (IngredientInline, )

    def get_favorites(self, recipe):
        return recipe.favorites.count()

    def get_ingredients(self, recipe):
        return ', '.join([
            ingredients.name for ingredients in recipe.ingredients.all()
        ])

    get_favorites.short_description = 'В избранном'
    get_ingredients.short_description = 'Продукты'


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

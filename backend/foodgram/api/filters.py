from django.contrib.admin import SimpleListFilter
from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if value and self.request.user.is_authenticated:
            return recipes.filter(shopping_cart__user=self.request.user)
        return


class CookingTimeFilter(SimpleListFilter):
    title = 'Время приготовления'
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return [
            ('fast', 'Быстрые'),
            ('medium', 'Средние'),
            ('slow', 'Долгие'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value() == 'fast':
            return queryset.distinct().filter(cooking_time__lte=15)
        if self.value() == 'medium':
            return queryset.distinct().filter(
                cooking_time__gt=15,
                cooking_time__lte=60
            )
        if self.value() == 'slow':
            return queryset.distinct().filter(
                cooking_time__gt=60
            )

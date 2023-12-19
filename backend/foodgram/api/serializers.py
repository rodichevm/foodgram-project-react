from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as DjosersUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag, User)


class UserSerializer(DjosersUserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, user):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return user.following.filter(user=request.user).exists()


class SubscribesSerializer(UserSerializer):
    recipes_count = serializers.ReadOnlyField(source='recipes.count')
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = (
            *UserSerializer.Meta.fields,
            'recipes_count',
            'recipes',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author_id = self.context.get(
            'request').parser_context.get('kwargs').get('id')
        author = get_object_or_404(User, id=author_id)
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=author_id):
            raise serializers.ValidationError(
                detail='Подписка уже существует',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise serializers.ValidationError(
                detail='Нельзя подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 10 ** 10))
        return RecipeShortSerializer(
            obj.recipes.all()[: limit], many=True, read_only=True).data


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=False, many=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientinrecipes',
        many=True
    )
    author = UserSerializer(many=False, read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_flagged(self, recipe, model):
        request = self.context.get('request')

        if not request or request.user.is_anonymous:
            return False

        return model.objects.filter(user=request.user, recipe=recipe).exists()

    def get_is_favorited(self, recipe):
        return self.get_flagged(recipe, Favorite)

    def get_is_in_shopping_cart(self, recipe):
        return self.get_flagged(recipe, ShoppingCart)

    def get_ingredients(self, recipe):
        ingredients = Ingredient.objects.filter(recipe=recipe)
        return IngredientAmountSerializer(ingredients, many=True).data


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientsCreateSerializer(many=True)
    cooking_time = serializers.IntegerField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    @staticmethod
    def validate_repeat_existence(items, model):
        invalid_items = [
            item.id if isinstance(item, Tag) else item['id']
            for item in items
            if not model.objects.filter(
                id=item.id if isinstance(item, Tag) else item[
                    'id']).exists()
        ]
        if invalid_items:
            raise serializers.ValidationError(
                {'Несуществующие элементы': invalid_items}
            )
        item_ids = [
            item.id if isinstance(item, Tag) else item['id']
            for item in items
        ]
        if len(items) != len(set(item_ids)):
            raise serializers.ValidationError(
                {'Повторяющиеся элементы': item_ids}
            )

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        self.validate_repeat_existence(tags, Tag)
        self.validate_repeat_existence(ingredients, Ingredient)
        if [item for item in ingredients if item['amount'] < 1]:
            raise serializers.ValidationError(
                'Минимальное количество продукта: 1')
        if data.get('cooking_time') < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время должно быть больше одной минуты'
            })
        return data

    def ingredients_create(self, ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        request = self.context.get('request', None)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.tags.set(tags)
        self.ingredients_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        self.ingredients_create(ingredients, instance)
        instance.tags.set(validated_data.pop('tags'))
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance,
            context=self.context,
        ).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class BaseUserRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        if user.shopping_carts.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в корзину')
        if user.favorites.filter(recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное')
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(BaseUserRecipeSerializer):
    class Meta(BaseUserRecipeSerializer.Meta):
        model = ShoppingCart


class FavoriteSerializer(BaseUserRecipeSerializer):
    class Meta(BaseUserRecipeSerializer.Meta):
        model = Favorite

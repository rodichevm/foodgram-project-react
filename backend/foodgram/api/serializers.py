from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer as DjosersUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import (
    Favorite, Follow, Ingredient, IngredientAmount,
    Recipe, ShoppingCart, Tag, User
)


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
        return user.follower.filter(user=request.user).exists()


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

    def get_recipes(self, subscribe):
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 10 ** 10))
        return RecipeShortSerializer(
            subscribe.recipes.all()[: limit],
            many=True,
            read_only=True
        ).data


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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.ingredient_id
        return representation


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
        return IngredientAmountSerializer(
            recipe.ingredientinrecipes.all(), many=True
        ).data


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
            item_id for item_id in items
            if not model.objects.filter(id=item_id).exists()
        ]
        if invalid_items:
            raise serializers.ValidationError(
                f'Несуществующие элементы для модели '
                f'{model._meta.verbose_name}: {invalid_items}'
            )
        duplicate_items = {
            item_id for item_id in items if items.count(item_id) > 1
        }
        if duplicate_items:
            raise serializers.ValidationError(
                f'Повторяющиеся элементы для модели '
                f'{model._meta.verbose_name}: {duplicate_items}'
            )

    def validate(self, data):
        tags = data.get('tags')
        ingredients = data.get('ingredients')

        self.validate_repeat_existence([tag.id for tag in tags], Tag)
        self.validate_repeat_existence(
            [item['id'] for item in ingredients], Ingredient
        )

        incorrect_ingredients = [
            item['id'] for item in ingredients if item['amount'] < 1
        ]
        if incorrect_ingredients:
            raise serializers.ValidationError(
                f'Количество у продуктов: {incorrect_ingredients} '
                f'должно быть не менее 1'
            )
        cooking_time = data.get('cooking_time')
        if cooking_time < 1:
            raise serializers.ValidationError(
                f'Время должно быть больше одной минуты. '
                f'Текущее значение: {cooking_time}.'
            )
        return data

    @staticmethod
    def ingredients_create(ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
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
        model = self.Meta.model
        if model.objects.filter(
            user=data['user'], recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                f'Рецепт уже добавлен в {model._meta.verbose_name}')
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

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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredients_ids = instance.ingredients.all().values_list('id',
                                                                 flat=True)
        representation['id'] = list(ingredients_ids)
        return representation


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
        item_ids = [
            item for item in items
        ]
        invalid_items = [
            item_id for item_id in item_ids
            if not model.objects.filter(id=item_id).exists()
        ]
        if invalid_items:
            raise serializers.ValidationError(
                {
                    f'Несуществующие элементы для модели '
                    f'{model._meta.verbose_name}': invalid_items
                }
            )
        duplicate_items = [
            item_id for item_id in set(item_ids)
            if item_ids.count(item_id) > 1
        ]
        if len(items) != len(set(item_ids)):
            raise serializers.ValidationError(
                {f'Повторяющиеся элементы для модели '
                 f'{model._meta.verbose_name}': duplicate_items}
            )

    def validate(self, data):
        tags = data.get('tags')
        tags_ids = {tag.id for tag in tags}
        self.validate_repeat_existence(tags_ids, Tag)

        ingredients = data.get('ingredients')
        ingredient_ids = {
            ingredient.get('id') for ingredient in [
                dict(item) for item in ingredients
            ]
        }
        self.validate_repeat_existence(ingredient_ids, Ingredient)

        if [item for item in ingredients if item['amount'] < 1]:
            raise serializers.ValidationError(
                {'ingredients': 'Количество продукта должно быть не менее 1'}
            )
        if data.get('cooking_time') < 1:
            raise serializers.ValidationError({
                'cooking_time': 'Время должно быть больше одной минуты'
            })
        return data

    @staticmethod
    def ingredients_create(ingredients, recipe):
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
        if ingredients:
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

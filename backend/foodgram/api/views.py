from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import Pagination
from api.permissions import IsAuthorOrSafePermission
from api.serializers import (
    CreateRecipeSerializer, FavoriteSerializer,
    IngredientSerializer, ReadRecipeSerializer,
    ShoppingCartSerializer, SubscribesSerializer,
    TagSerializer, UserSerializer
)
from api.utils import generate_shopping_cart_message
from recipes.models import (
    Favorite, Follow,
    Ingredient, Recipe,
    ShoppingCart, Tag, User
)


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            serializer = SubscribesSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(
                Follow, user=user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(subscriptions)
        serializer = SubscribesSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = (IsAuthorOrSafePermission,)
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReadRecipeSerializer
        return CreateRecipeSerializer

    @staticmethod
    def add_recipe_to(request, pk, serializer):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = serializer(
            data={
                'user': request.user.id,
                'recipe': recipe.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def destroy_recipe_from(request, pk, model):
        get_object_or_404(
            model,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()

    @action(detail=False, methods=['GET'])
    def download_shopping_cart(self, request):
        return FileResponse(
            generate_shopping_cart_message(
                Recipe.create_shopping_cart_list(self.request.user)
            ),
            content_type='text/plain'
        )

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        return self.add_recipe_to(request, pk, ShoppingCartSerializer)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        return self.add_recipe_to(request, pk, FavoriteSerializer)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        self.destroy_recipe_from(request, pk, ShoppingCart)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        self.destroy_recipe_from(request, pk, Favorite)
        return Response(status=status.HTTP_204_NO_CONTENT)

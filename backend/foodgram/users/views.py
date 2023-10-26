from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import viewsets

from api.pagination import CustomPagination
from users.serializers import CustomUserSerializer

User = get_user_model()


class UsersViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination


class SubscriptionsViewSet(viewsets.ModelViewSet):
    pass


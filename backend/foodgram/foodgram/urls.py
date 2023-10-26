from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from users.views import UsersViewSet

router = routers.DefaultRouter()
router.register('users', UsersViewSet)
# router.register('subscriptions', SubscriptionsViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include('users.urls')),
    path('admin/', admin.site.urls)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

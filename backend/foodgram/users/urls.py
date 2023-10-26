from django.contrib import admin
from django.template.defaulttags import url
from django.urls import include, path, re_path

urlpatterns = [
    path('', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken'))
]

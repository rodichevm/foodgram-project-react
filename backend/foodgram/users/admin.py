from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email'
    )
    search_fields = ('username', 'email')
    list_filter = ('first_name', 'email')
    ordering = ('username',)
    empty_value_display = '-пусто-'

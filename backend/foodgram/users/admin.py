from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = (
        'id',
        'first_name',
        'last_name',
        'email'
    )
    search_fields = ('username', 'email')
    ist_filter = ('first_name', 'last_name')
    ordering = ('username',)
    empty_value_display = '-пусто-'

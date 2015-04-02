from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import AuthUser, LoggedLogin


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'date_joined',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'creation_ip',
            'creation_user_agent',
            )
    search_fields = ['first_name', 'last_name', 'email', ]
    list_filter = ('is_active', 'is_staff', 'is_superuser', )


@admin.register(LoggedLogin)
class LoggedLoginAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'login_at',
            'auth_user',
            'ip_address',
            'user_agent',
    )
    raw_id_fields = ('auth_user', )
    search_fields = ['ip_address', 'user_agent', ]


# unregister the Group model from admin since we're not using Django's built-in permissions
admin.site.unregister(Group)

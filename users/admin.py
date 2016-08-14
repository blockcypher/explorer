from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import AuthUser, LoggedLogin


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    def emails_sent(self, instance):
        return instance.sentemail_set.count()

    def address_subscriptions(self, instance):
        return instance.addresssubscription_set.count()

    def forwarding_addresses(self, instance):
        return instance.addressforwarding_set.count()

    list_display = (
            'id',
            'date_joined',
            'email',
            'emails_sent',
            'address_subscriptions',
            'forwarding_addresses',
            'first_name',
            'last_name',
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

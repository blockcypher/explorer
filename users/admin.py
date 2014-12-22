from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import GithubProfile, AuthUser, LoggedLogin, BlockcypherToken


@admin.register(AuthUser)
class AuthUserAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'date_joined',
            'first_name',
            'last_name',
            'email',
            'github_profile',
            'is_active',
            'is_staff',
            'is_superuser',
            )
    raw_id_fields = ('github_profile', )


@admin.register(GithubProfile)
class GithubProfileAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'added_at',
            'github_id',
            'github_created_at',
            'github_updated_at',
            'github_username',
            'primary_email',
            'full_name',
            'followers_cnt',
            'following_cnt',
            'public_repo_cnt',
            'public_gists_cnt',
            )


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


@admin.register(BlockcypherToken)
class BlockcypherTokenAdmin(admin.ModelAdmin):
    list_display = (
            'id',
            'created_at',
            'auth_user',
            'email_used',
    )
    raw_id_fields = ('auth_user', )


# unregister the Group model from admin since we're not using Django's built-in permissions
admin.site.unregister(Group)

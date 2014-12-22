from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse_lazy

from utils import get_client_ip

# For more info, see the django docs here:
# https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#a-full-example


class AuthUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a user with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email))
        if not password:
            # Create random and unknowable password
            password = self.make_random_password(length=15)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_staff = True
        user.save()

        return user


class GithubProfile(models.Model):
    added_at = models.DateTimeField(auto_now_add=True, db_index=True)
    github_id = models.IntegerField(blank=False, null=False, db_index=True)
    github_created_at = models.DateTimeField(null=False, db_index=True)
    github_updated_at = models.DateTimeField(null=False, db_index=True)
    github_username = models.CharField(max_length=256, blank=False, null=False, db_index=True)
    primary_email = models.EmailField(max_length=128, unique=True)
    full_name = models.CharField(max_length=128, blank=True, db_index=True)
    followers_cnt = models.IntegerField(blank=False, null=False, db_index=True)
    following_cnt = models.IntegerField(blank=False, null=False, db_index=True)
    public_repo_cnt = models.IntegerField(blank=False, null=False, db_index=True)
    public_gists_cnt = models.IntegerField(blank=False, null=False, db_index=True)


class AuthUser(AbstractBaseUser):
    date_joined = models.DateTimeField(auto_now_add=True, db_index=True)
    email = models.EmailField(max_length=128, unique=True)
    github_profile = models.OneToOneField(GithubProfile, blank=True, null=True)

    is_active = models.BooleanField(default=True, help_text='Can login?')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = AuthUserManager()

    USERNAME_FIELD = 'email'

    @property
    def is_superuser(self):
        # FIXME
        return self.is_superuser

    def __str__(self):
        return '%s: %s' % (self.id, self.email)

    def get_full_name(self):
        # May be null
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.self.first_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # FIXME
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # FIXME
        return self.is_superuser

    def get_login_uri(self):
        return '%s?e=%s' % (reverse_lazy('user_login'), self.email)


class LoggedLogin(models.Model):
    login_at = models.DateTimeField(auto_now_add=True, db_index=True)
    auth_user = models.ForeignKey(AuthUser, blank=False, null=False)
    ip_address = models.IPAddressField(null=False, blank=False, db_index=True)
    user_agent = models.CharField(max_length=1024, blank=True, db_index=True)

    def __str__(self):
        return '%s: %s' % (self.id, self.ip_address)

    @classmethod
    def record_login(cls, request):
        return cls.objects.create(
                auth_user=request.user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                )


class BlockypherToken(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    auth_user = models.ForeignKey(AuthUser, blank=False, null=False)
    email_used = models.EmailField(max_length=128, unique=True, blank=False, null=False)

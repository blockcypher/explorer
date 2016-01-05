from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse_lazy

from emails.trigger import send_and_log

from utils import get_client_ip, get_user_agent


# For more info, see the django docs here:
# https://docs.djangoproject.com/en/1.7/topics/auth/customizing/#a-full-example


class AuthUserManager(BaseUserManager):
    def create_user(self, email, password, creation_ip, creation_user_agent):
        """
        Creates and saves a user with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        # force whole email to lowercase. violates spec but better usability.
        user = self.model(email=email.lower().strip())
        # if no password it calls set_unusuable_password() under the hood:
        user.set_password(password)
        user.creation_ip = creation_ip
        user.creation_user_agent = creation_user_agent
        user.save()

        return user

    def create_superuser(self, email, password, creation_ip=None,
            creation_user_agent=None):
        """
        Creates and saves a superuser with the given email and password.
        """
        if not creation_ip:
            creation_ip = '127.0.0.1'
        if not creation_user_agent:
            creation_user_agent = 'admin'

        user = self.create_user(
                email=email,
                password=password,
                creation_ip=creation_ip,
                creation_user_agent=creation_user_agent,
                )
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class AuthUser(AbstractBaseUser):
    date_joined = models.DateTimeField(auto_now_add=True, db_index=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)

    email = models.EmailField(max_length=128, unique=True)

    is_active = models.BooleanField(default=True, help_text='Can login?')
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    creation_ip = models.IPAddressField(null=False, blank=False, db_index=True)
    creation_user_agent = models.CharField(max_length=1024, blank=True, db_index=True)

    email_verified = models.BooleanField(default=False, db_index=True)

    objects = AuthUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return '%s: %s' % (self.id, self.email)

    def get_full_name(self):
        if self.first_name and self.last_name:
            return '%s %s' % (self.first_name, self.last_name)
        else:
            return ''

    def get_short_name(self):
        return self.first_name

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

    def get_address_subscriptions(self):
        return self.addresssubscription_set.filter(
                unsubscribed_at=None,
                disabled_at=None,
                ).order_by('-id')

    def get_address_forwardings(self):
        return self.addressforwarding_set.filter(archived_at=None).order_by('-id')

    def send_pwreset_email(self):
        """
        Send password reset email to user.
        """
        # TODO: add some sort of throttling
        return send_and_log(
                subject='Blockcypher Password Reset',
                body_template='password_reset.html',
                to_user=self,
                body_context={},
                fkey_objs={'auth_user': self},
                )


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
                user_agent=get_user_agent(request),
                )

from django.db import models

from django.utils.timezone import now

from jsonfield import JSONField

from utils import get_user_agent, get_client_ip


class SentEmail(models.Model):

    sent_at = models.DateTimeField(auto_now_add=True, db_index=True)
    from_email = models.EmailField(max_length=256, null=False, blank=False, db_index=True)
    from_name = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    to_email = models.EmailField(max_length=256, null=False, blank=False, db_index=True)
    to_name = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    cc_email = models.EmailField(max_length=256, null=True, blank=True, db_index=True)
    cc_name = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    body_template = models.CharField(max_length=256, null=False, db_index=True)
    body_context = JSONField()
    subject = models.TextField(null=False, blank=False)
    unsub_code = models.CharField(max_length=64, blank=False, null=False, unique=True, db_index=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    unsub_ip = models.IPAddressField(null=False, blank=False, db_index=True)
    unsub_ua = models.CharField(max_length=1024, blank=True, db_index=True)
    verif_code = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True, db_index=True)
    verif_ip = models.IPAddressField(null=False, blank=False, db_index=True)
    verif_ua = models.CharField(max_length=1024, blank=True, db_index=True)

    # optional FK:
    auth_user = models.ForeignKey('users.AuthUser', null=True, blank=True)
    address_subscription = models.ForeignKey('addresses.AddressSubscription', null=True, blank=True)
    transaction_notification = models.ForeignKey('transactions.AddressSubscription', null=True, blank=True)

    def __str__(self):
        return '%s to %s' % (self.id, self.to_email)

    def verify_user_email(self, request):
        self.verified_at = now()
        self.verif_ua = get_user_agent(request)
        self.verif_ip = get_client_ip(request)
        self.save()

        auth_user = self.auth_user
        auth_user.email_verified = True
        auth_user.save()

from django.db import models
from jsonfield import JSONField


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
    verif_code = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True, db_index=True)
    verif_ip = models.IPAddressField(null=False, blank=False, db_index=True)

    # optional FK:
    auth_user = models.ForeignKey('users.AuthUser', null=True, blank=True)
    address_subscription = models.ForeignKey('addresses.AddressSubscription', null=True, blank=True)
    transaction_notification = models.ForeignKey('transactions.AddressSubscription', null=True, blank=True)

    def __str__(self):
        return '%s to %s' % (self.id, self.to_email)

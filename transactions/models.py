from django.db import models


class TransactionEvent(models.Model):
    '''
    Transaction events generated from an address subscription
    '''
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    tx_hash = models.CharField(blank=False, null=False, max_length=128, db_index=True)
    b58_address = models.CharField(blank=False, null=False, max_length=64, db_index=True)
    address_subscription = models.ForeignKey('addresses.AddressSubscription', blank=False, null=False)

    def __str__(self):
        return '%s to %s' % (self.id, self.tx_hash)

    def send_notification(self):
        # FIXME
        pass

from django.db import models


class TransactionEvent(models.Model):
    '''
    Transaction events generated from an address subscription
    '''
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    tx_hash = models.CharField(blank=False, null=False, max_length=128, db_index=True)
    address_subscription = models.ForeignKey('addresses.AddressSubscription', blank=False, null=False)
    conf_num = models.IntegerField(blank=False, null=False, db_index=True)
    double_spend = models.BooleanField(db_index=True, default=False)

    def __str__(self):
        return '%s to %s' % (self.id, self.tx_hash)

    def send_double_spend_notification(self):
        # FIXME
        pass

    def send_unconfirmed_tx_email(self):
        # FIXME
        pass

    def send_confirmed_tx_email(self):
        # FIXME
        pass

    def send_email_notification(self):
        if self.double_spend:
            self.send_double_spend_notification()

        if self.conf_num == 0:
            self.send_unconfirmed_tx_email()

        if self.conf_num == 6:
            self.send_confirmed_tx_email()

        # Do nothing for rest of cases
        return

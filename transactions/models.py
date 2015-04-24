from django.db import models

from blockcypher.utils import satoshis_to_btc_rounded

from emails.trigger import send_and_log


class OnChainTransaction(models.Model):
    '''
    Transaction events generated from an address subscription
    '''
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    tx_hash = models.CharField(blank=False, null=False, max_length=128, db_index=True)
    address_subscription = models.ForeignKey('addresses.AddressSubscription', blank=False, null=False)
    num_confs = models.IntegerField(blank=False, null=False, db_index=True)
    double_spend = models.BooleanField(db_index=True, default=False)
    satoshis_sent = models.BigIntegerField(blank=False, null=False, db_index=True)
    fee_in_satoshis = models.BigIntegerField(blank=False, null=False, db_index=True)

    def __str__(self):
        return '%s to %s' % (self.id, self.tx_hash)

    def send_double_spend_tx_notification(self):
        # FIXME
        pass

    def send_unconfirmed_tx_email(self):
        b58_address = self.address_subscription.b58_address
        context_dict = {
                'b58_address': b58_address,
                'coin_symbol': self.address_subscription.coin_symbol,
                'sent_in_btc': satoshis_to_btc_rounded(self.satoshis_sent),
                'fee_in_btc': satoshis_to_btc_rounded(self.fee_in_satoshis),
                'currency_display_name': self.address_subscription.get_currency_display_name(),
                'currency_abbrev': self.address_subscription.get_currency_abbrev(),
                'tx_hash': self.tx_hash,
                'num_confs': self.num_confs,
                }
        if self.address_subscription.address_forwarding_obj:
                context_dict['destination_address'] = self.address_subscription.address_forwarding_obj.destination_address
                context_dict['satoshis_transacted'] = self.satoshis_sent
        fkey_objs = {
                'transaction_event': self,
                'address_subscription': self.address_subscription,
                }
        return send_and_log(
                subject='Unconfirmed Transaction for %s' % b58_address,
                body_template='new_tx.html',
                to_user=self.address_subscription.auth_user,
                body_context=context_dict,
                fkey_objs=fkey_objs,
                )

    def send_confirmed_tx_email(self):
        b58_address = self.address_subscription.b58_address
        context_dict = {
                'b58_address': b58_address,
                'coin_symbol': self.address_subscription.coin_symbol,
                'tx_hash': self.tx_hash,
                'num_confs': self.num_confs,
                'currency_display_name': self.address_subscription.get_currency_display_name(),
                }
        fkey_objs = {
                'transaction_event': self,
                'address_subscription': self.address_subscription,
                }
        return send_and_log(
                subject='Transaction %s... Confirmed' % self.tx_hash[:10],
                body_template='confirmed_tx.html',
                to_user=self.address_subscription.auth_user,
                body_context=context_dict,
                fkey_objs=fkey_objs,
                )

    def is_subscribed(self):
        return self.address_subscription.is_active()

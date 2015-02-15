from django.db import models

from blockcypher.constants import COIN_CHOICES, COIN_SYMBOL_MAPPINGS

from emails.trigger import send_and_log


class AddressSubscription(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    coin_symbol = models.CharField(choices=COIN_CHOICES, max_length=16, null=False, blank=False, db_index=True)
    b58_address = models.CharField(blank=False, null=False, max_length=64, db_index=True)
    notify_on_broadcast = models.BooleanField(db_index=True, default=True)
    notify_on_first_confirm = models.BooleanField(db_index=True, default=True)
    notify_on_sixth_confirm = models.BooleanField(db_index=True, default=False)
    notify_on_deposit = models.BooleanField(db_index=True, default=True)
    notify_on_withdrawal = models.BooleanField(db_index=True, default=True)
    auth_user = models.ForeignKey('users.AuthUser', blank=False, null=False)
    blockcypher_id = models.CharField(choices=COIN_CHOICES, max_length=64, null=False, blank=False, db_index=True)

    def __str__(self):
        return '%s to %s' % (self.id, self.b58_address)

    def send_welcome_email(self):
        b58_address = self.b58_address
        context_dict = {
                'b58_address': b58_address,
                'cs_display': COIN_SYMBOL_MAPPINGS[self.coin_symbol]['display_name']
                }
        fkey_objs = {
                'address_subscription': self,
                'auth_user': self.auth_user,
                }
        return send_and_log(
                subject='Please Confirm Your Email Subscription to %s' % b58_address,
                body_template='new_user_confirmation.html',
                to_email=self.auth_user.email,
                to_name=self.auth_user.get_full_name(),
                body_context=context_dict,
                fkey_objs=fkey_objs,
                )

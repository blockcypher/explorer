from django import forms
from django.utils.translation import ugettext_lazy as _

from blockcypher.constants import COIN_CHOICES, COIN_SYMBOL_MAPPINGS
from blockcypher.utils import is_valid_address_for_coinsymbol


class KnownUserAddressSubscriptionForm(forms.Form):

    # TODO: add advanced granulatiry for confirms (broadcast/1/6), amount, & send/receive

    coin_address = forms.CharField(
        label=_('Address to Subscribe To'),
        required=True,
        min_length=25,
        max_length=35,
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'}),
    )

    coin_symbol = forms.ChoiceField(
        label=_('Network'),
        required=True,
        choices=COIN_CHOICES,
    )

    def clean_coin_address(self):
        address = self.cleaned_data.get('coin_address')
        if not address:
            return None
        return address.strip()

    def clean(self):
        address = self.cleaned_data.get('coin_address')
        if not address:
            return None
        coin_symbol = self.cleaned_data.get('coin_symbol')
        if address and coin_symbol:
            if not is_valid_address_for_coinsymbol(address, coin_symbol=coin_symbol):
                cs_display = COIN_SYMBOL_MAPPINGS[coin_symbol]['display_name']
                msg = _("Sorry, that's not a valid address for %(coin_symbol)s" % {'coin_symbol': cs_display})
                raise forms.ValidationError(msg)

        return self.cleaned_data


class NewUserAddressSubscriptionForm(KnownUserAddressSubscriptionForm):
    email = forms.EmailField(
        label=_('Email to Receive Notices'),
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'me@example.com', 'class': 'input-lg'}),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.lower().strip()


class AddressSearchForm(KnownUserAddressSubscriptionForm):

    def __init__(self, *args, **kwargs):
        super(AddressSearchForm, self).__init__(*args, **kwargs)
        self.fields['coin_address'].label = _("Address")


class KnownUserAddressForwardingForm(KnownUserAddressSubscriptionForm):
    wants_email_notification = forms.BooleanField(
        label=_('Receive Email Notification for Transactions'),
        initial=True,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(KnownUserAddressForwardingForm, self).__init__(*args, **kwargs)
        self.fields['coin_address'].label = _("Address to Forward To")
        self.fields['coin_address'].help_text = _('We will generate a new address that will automatically forward to this address')


class NewUserAddressForwardingForm(NewUserAddressSubscriptionForm):

    def __init__(self, *args, **kwargs):
        super(NewUserAddressForwardingForm, self).__init__(*args, **kwargs)
        self.fields['coin_address'].label = _("Address to Forward To")
        self.fields['coin_address'].help_text = _('We will generate a new address that will automatically forward to this address')
        self.fields['email'].required = False
        self.fields['email'].label = _('Email to Receive Notices (strongly recommended)')
        self.fields['email'].help_text = _('If you do not supply an email address, you will have to monitor the Blockchain yourself for incoming transactions')

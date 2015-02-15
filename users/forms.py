from django import forms
from django.utils.translation import ugettext_lazy as _


from blockcypher.constants import COIN_CHOICES
from blockcypher.utils import is_valid_address_for_coinsymbol


class LoginForm(forms.Form):
    email = forms.CharField(
        label=_('Email'),
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'me@example.com',
            'autofocus': 'autofocus',
            'class': 'input-lg',
            }),
    )
    password = forms.CharField(
        label=_('Password'),
        required=True,
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}, render_value=False)
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.lower().strip()


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'me@example.com', 'class': 'input-lg'}),
    )
    password = forms.CharField(
        required=True,
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        required=True,
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=8,
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        return self.cleaned_data['email'].lower().strip()

    def clean(self):
        pw = self.cleaned_data.get('password')
        pwc = self.cleaned_data.get('password_confirm')
        if pw != pwc:
            err_msg = _('Those passwords did not match. Please try again.')
            raise forms.ValidationError(err_msg)
        else:
            return self.cleaned_data


class CoinSymbolForm(forms.Form):
    coin_symbol = forms.ChoiceField(
            label=_('Blockchain'),
            required=True,
            choices=COIN_CHOICES,
            widget=forms.Select(attrs={'onchange': 'this.form.submit()', 'class': 'input-lg'}),
        )


class BCYFaucetForm(forms.Form):
    btc_to_send = forms.DecimalField(
            label=_('BTC to Send'),
            max_value=.1,
            required=True,
            widget=forms.TextInput(attrs={
                'autofocus': 'autofocus',
                }),
        )
    address_to_fund = forms.CharField(
            label=_('Blockcypher Testnet Address'),
            required=False,
            min_length=27,
            max_length=34,
            help_text=_('If blank we will create one for you but you will not have the private key.'),
            widget=forms.TextInput(),
    )

    def clean_address_to_fund(self):
        address = self.cleaned_data.get('address_to_fund').strip()
        if address and not is_valid_address_for_coinsymbol(address, coin_symbol='bcy'):
            msg = _("Sorry, that's not a valid Blockcypher (not bitcoin) Testnet address")
            raise forms.ValidationError(msg)

        return address

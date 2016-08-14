from django import forms
from django.utils.translation import ugettext_lazy as _


from blockcypher.constants import COIN_CHOICES


class LoginForm(forms.Form):
    email = forms.EmailField(
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


class PWResetForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'me@example.com',
            'autofocus': 'autofocus',
            'class': 'input-lg',
            }),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.lower().strip()


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'me@example.com',
            'autofocus': 'autofocus',
            'class': 'input-lg',
            }),
    )
    password = forms.CharField(
        required=True,
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=12,
    )
    password_confirm = forms.CharField(
        required=True,
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=12,
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


class SetPWForm(forms.Form):
    password = forms.CharField(
        required=True,
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'input-lg',
            'autofocus': 'autofocus',
            }),
        min_length=12,
    )
    password_confirm = forms.CharField(
        required=True,
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=12,
    )

    def __init__(self, *args, **kwargs):
        super(SetPWForm, self).__init__(*args, **kwargs)

    def clean(self):
        pw = self.cleaned_data.get('password')
        pwc = self.cleaned_data.get('password_confirm')
        if pw != pwc:
            err_msg = _('Those passwords did not match. Please try again.')
            raise forms.ValidationError(err_msg)
        else:
            return self.cleaned_data


class ChangePWForm(forms.Form):

    oldpassword = forms.CharField(
            required=True,
            label=_('Current Password'),
            widget=forms.PasswordInput(attrs={
                'autocomplete': 'off',
                'autofocus': 'autofocus',
                }),
            help_text=_('Your existing password that you no longer want to use'),
    )

    newpassword = forms.CharField(
            required=True,
            label=_('New Password'),
            widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
            min_length=12,
            help_text=_('Please choose a new secure password'),
    )

    newpassword_confirm = forms.CharField(
            required=True,
            label=_('Confirm New Password'),
            widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePWForm, self).__init__(*args, **kwargs)

    def clean_oldpassword(self):
        password = self.cleaned_data['oldpassword']
        if not self.user.check_password(password):
            raise forms.ValidationError(_('Sorry, that password is not correct'))
        return password

    def clean(self):
        if self.cleaned_data.get('newpassword') != self.cleaned_data.get('newpassword_confirm'):
            raise forms.ValidationError(_('Your new passwords did not match.  Please try again.'))
        if self.cleaned_data.get('newpassword') == self.cleaned_data.get('oldpassword'):
            raise forms.ValidationError(_('Your old password matches your new password. Your password was not changed.'))
        else:
            return self.cleaned_data

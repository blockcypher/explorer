from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from annoying.functions import get_object_or_None


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
        min_length=10,
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}, render_value=False)
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.lower().strip()


class RegistrationForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'me@example.com', 'class': 'input-lg'}),
        min_length=10,
    )
    password = forms.CharField(
        required=True,
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=6,
    )
    password_confirm = forms.CharField(
        required=True,
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={'class': 'input-lg'}),
        min_length=6,
    )

    def __init__(self, AuthUser=None, *args, **kwargs):
        self.AuthUser = AuthUser
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        existing_user = get_object_or_None(self.AuthUser, email=email)
        if existing_user:
            login_uri = existing_user.get_login_uri()
            msg = _('That email already belongs to someone, do you want to <a href="%(login_uri)s">login</a>?') % {'login_uri': login_uri}
            raise forms.ValidationError(mark_safe(msg))

        if len(email) > 100:
            msg = _('Sorry, your email address must be less than 100 characters')
            raise forms.ValidationError(msg)
        return email

    def clean(self):
        pw = self.cleaned_data.get('password')
        pwc = self.cleaned_data.get('password_confirm')
        if pw != pwc:
            err_msg = _('Those passwords did not match. Please try again.')
            raise forms.ValidationError(err_msg)
        else:
            return self.cleaned_data

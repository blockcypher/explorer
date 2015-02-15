from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.shortcuts import get_object_or_404

from annoying.functions import get_object_or_None
from annoying.decorators import render_to

from users.models import AuthUser, LoggedLogin
from emails.models import SentEmail

from users.forms import LoginForm, RegistrationForm

from utils import get_client_ip, get_user_agent


@render_to('login.html')
def user_login(request):
    """
    Email/pass logins, github logins are processed separately via github_authorized
    """
    user = request.user
    if user.is_authenticated():
        # TODO: notification
        return HttpResponseRedirect(reverse_lazy('dashboard'))

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user_found = get_object_or_None(AuthUser, email=email)
            if hasattr(user_found, 'github_profile') and user_found.github_profile:
                return HttpResponseRedirect(reverse_lazy('github_login'))

            if user_found:
                user = authenticate(email=email, password=password)
                if user:
                    login(request, user)
                    LoggedLogin.record_login(request)
                    if user.is_staff:
                        return HttpResponseRedirect('/admin/')
                    else:
                        post_login_url = reverse_lazy('dashboard')
                        return HttpResponseRedirect(post_login_url)
                else:
                    msg = _("Sorry, that password is incorrect.")
                    messages.warning(request, msg, extra_tags='safe')
            else:
                signup_base = reverse_lazy('signup')
                signup_url = '%s?e=%s' % (signup_base, escape(email))
                msg = _('Account not found. Did you mean to <a href="%(signup_url)s">sign up</a>?' % {'signup_url': signup_url})
                messages.warning(request, msg, extra_tags='safe')
    elif request.method == 'GET':
        email = request.GET.get('e')
        if email:
            form = LoginForm(initial={'email': email})
    return {
            'form': form,
            'is_login_page': True,
            }


@render_to('signup.html')
def signup(request):
    user = request.user
    if user.is_authenticated():
        return HttpResponseRedirect(reverse_lazy('dashboard'))
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            existing_user = get_object_or_None(AuthUser, email=email)

            if existing_user:
                msg = _('That email already belongs to someone, please login:')
                messages.warning(request, msg)
                return HttpResponseRedirect(existing_user.get_login_uri())

            else:
                # create user
                user = AuthUser.objects.create_user(
                        email=email.lower(),
                        password=password,
                        creation_ip=get_client_ip(request),
                        creation_user_agent=get_user_agent(request),
                )

                # login user
                user_to_login = authenticate(email=email, password=password)
                login(request, user_to_login)

                # Log the login
                LoggedLogin.record_login(request)

                msg = _('Login Succesful')
                messages.success(request, msg)

                return HttpResponseRedirect(reverse_lazy('dashboard'))

    elif request.method == 'GET':
        # Preseed name and/or email if passed through GET string
        email = request.GET.get('e')
        full_name = request.GET.get('name')
        if email or full_name:
            form = RegistrationForm(initial={
                'email': email,
                'full_name': full_name,
                })

    return {
            'form': form,
            'is_signup_page': True,
            }


def confirm_subscription(request, verif_code):
    sent_email = get_object_or_404(SentEmail, verif_code=verif_code)
    auth_user = sent_email.auth_user

    # Login the user
    # http://stackoverflow.com/a/3807891/1754586
    auth_user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, auth_user)

    # Log the login
    LoggedLogin.record_login(request)

    if sent_email.verified_at and auth_user.is_email_verified:
        # already verified
        msg = _('<b>%(email_address)s</b> already verified' % {'email_address': sent_email.to_email})
        messages.info(request, msg, extra_tags='safe')
    else:
        # not yet verified
        sent_email.verify_user_email()

        msg = _('<b>%(email_address)s</b> verified. You will now receive notifcations for %(b58_address)s' % {
            'email_address': sent_email.to_email,
            'b58_address': sent_email.address_subscription.b58_address,
            })
        messages.info(request, msg, extra_tags='safe')

    return HttpResponseRedirect(reverse_lazy('dashboard'))


@login_required
@render_to('dashboard.html')
def dashboard(request):
    return {}


def logout_request(request):
    " Log a user out using Django's logout function and redirect them "
    logout(request)
    msg = _("You Are Now Logged Out")
    messages.success(request, msg)
    return HttpResponseRedirect(reverse_lazy('user_login'))


def fail500(request):
    raise Exception('IntentionalFail: This Was On Purpose')

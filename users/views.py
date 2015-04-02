from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.html import escape
from django.shortcuts import get_object_or_404

from annoying.functions import get_object_or_None
from annoying.decorators import render_to

from users.models import AuthUser, LoggedLogin
from emails.models import SentEmail

from users.forms import LoginForm, RegistrationForm, SetPWForm, ChangePWForm, PWResetForm

from datetime import timedelta

from utils import get_client_ip, get_user_agent


@render_to('login.html')
def user_login(request):
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

            auth_user = get_object_or_None(AuthUser, email=email)
            if auth_user:
                if auth_user.has_usable_password():
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
                        pw_reset_uri = reverse_lazy('forgot_password')
                        pw_reset_uri = '%s?e=%s' % (pw_reset_uri, escape(email))
                        msg = _('Sorry, that password is incorrect. Would you like to <a href="%(pw_reset_uri)s">reset your password</a>?' % {
                            'pw_reset_uri': pw_reset_uri,
                            })
                        messages.warning(request, msg, extra_tags='safe')
                else:
                    msg = _("Sorry, that account doesn't have a password set yet.")
                    messages.info(request, msg, extra_tags='safe')
                    redir_uri = reverse_lazy('forgot_password')
                    redir_uri = '%s?e=%s' % (redir_uri, escape(email))
                    return HttpResponseRedirect(redir_uri)

            else:
                signup_base = reverse_lazy('signup')
                signup_uri = '%s?e=%s' % (signup_base, escape(email))
                msg = _('Account not found. Did you mean to <a href="%(signup_uri)s">sign up</a>?' % {
                    'signup_uri': signup_uri,
                    })
                messages.warning(request, msg, extra_tags='safe')
    elif request.method == 'GET':
        email = request.GET.get('e')
        if email:
            form = LoginForm(initial={'email': email})

    return {'form': form}


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
            }


@login_required
@render_to('change_pw.html')
def change_password(request):
    user = request.user
    form = ChangePWForm(user=user)
    if request.method == 'POST':
        form = ChangePWForm(user=user, data=request.POST)
        if form.is_valid():
            new_pw = form.cleaned_data['newpassword']
            user.set_password(new_pw)
            user.save()

            msg = _('Your password has been changed.')
            messages.success(request, msg, extra_tags='safe')

            return HttpResponseRedirect(reverse_lazy('home'))

    return {'form': form}


@login_required
@render_to('password_upsell.html')
def password_upsell(request):

    # safety check - users who already have passwords can't use this flow
    if request.user.has_usable_password() and request.method == 'GET':
        msg = _('Password Already Set')
        messages.info(request, msg)
        return HttpResponseRedirect(reverse_lazy('dashboard'))

    form = SetPWForm()
    if request.method == 'POST':
        form = SetPWForm(data=request.POST)
        if form.is_valid():
            pw = form.cleaned_data['password']
            user = request.user
            user.set_password(pw)
            user.save()

            msg = _('Password Set')
            messages.success(request, msg)

            # (Re)login the user, since setting password logs them out
            user = authenticate(email=user.email, password=pw)
            login(request, user)

            return HttpResponseRedirect(reverse_lazy('dashboard'))

    return {'form': form}


@render_to('reset_pw.html')
def reset_pw(request, verif_code):
    '''
    Page you arrive on after clicking a link to (re)set your password
    '''
    sent_email = get_object_or_404(SentEmail, verif_code=verif_code)

    if now() - sent_email.sent_at > timedelta(hours=72):
        msg = _('Sorry, that link has expired. Please try again.')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse_lazy('forgot_password'))

    if sent_email.verified_at and (now() - sent_email.verified_at > timedelta(minutes=60)):
        msg = _('Sorry, that was already used. Please try again.')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse_lazy('forgot_password'))

    else:
        form = SetPWForm()
        if request.method == 'POST':
            form = SetPWForm(data=request.POST)
            if form.is_valid():
                sent_email.verify_user_email(request)

                password = form.cleaned_data['password']
                auth_user = sent_email.auth_user

                auth_user.set_password(password)
                auth_user.save()

                msg = _('Your password has been set.')
                messages.success(request, msg)

                # login user
                user_to_login = authenticate(email=auth_user.email, password=password)
                login(request, user_to_login)

                # Log the login
                LoggedLogin.record_login(request)

                # All done
                return HttpResponseRedirect(reverse_lazy('dashboard'))

    return {
            # 'user': sent_email.auth_user,
            'form': form,
            'verif_code': verif_code,
            }


@render_to('forgot_pw.html')
def forgot_password(request):
    '''
    Page for users who forgot (or never set) their password and aren't logged in
    '''

    form = PWResetForm()

    if request.method == 'POST':
        form = PWResetForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            auth_user = get_object_or_None(AuthUser, email=email)
            if auth_user:
                auth_user.send_pwreset_email()
                kwargs = {'email_address': email}
                redir_url = reverse_lazy('confirm_pw_reset', kwargs=kwargs)
                return HttpResponseRedirect(redir_url)
            else:
                signup_url = reverse_lazy('signup')
                signup_url = '%s?e=%s' % (signup_url, escape(email))
                msg = _('Sorry, no user found with that email. Would you like to <a href="%(signup_url)s">create an account</a>?' % {
                    'signup_url': signup_url})
                messages.warning(request, msg, extra_tags='safe')

    elif request.method == 'GET':
        email = request.GET.get('e')
        if email:
            form = PWResetForm(initial={'email': email})

    return {'form': form}


def confirm_subscription(request, verif_code):
    '''
    New user onboarding where they confirm their email and then we ask for a PW
    '''
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
        return HttpResponseRedirect(reverse_lazy('dashboard'))

    else:
        # not yet verified
        sent_email.verify_user_email(request)

        msg = _('<b>%(email_address)s</b> verified, you will now receive email notifcations for <b>%(b58_address)s</b>.' % {
            'email_address': sent_email.to_email,
            'b58_address': sent_email.address_subscription.b58_address,
            })
        messages.info(request, msg, extra_tags='safe')

        # Ask them to create a new PW
        return HttpResponseRedirect(reverse_lazy('password_upsell'))


@login_required
@render_to('dashboard.html')
def dashboard(request):
    user = request.user
    return {
            'user': user,
            'address_subscriptions': user.get_address_subscriptions(),
            }


@login_required
@render_to('unconfirmed_email.html')
def unconfirmed_email(request):
    user = request.user
    if user.email_verified:
        # User actually is confirmed
        return HttpResponseRedirect(reverse_lazy('dashboard'))
    else:
        return {'user': user}


@render_to('confirm_pw_reset.html')
def confirm_pw_reset(request, email_address):
    auth_user = get_object_or_404(AuthUser, email=email_address)
    return {'user': auth_user}


def logout_request(request):
    " Log a user out using Django's logout function and redirect them "
    logout(request)
    msg = _("You Are Now Logged Out")
    messages.success(request, msg)
    return HttpResponseRedirect(reverse_lazy('user_login'))


def fail500(request):
    raise Exception('IntentionalFail: This Was On Purpose')

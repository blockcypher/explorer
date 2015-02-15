from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from annoying.functions import get_object_or_None
from annoying.decorators import render_to

from tokens.settings import GH_CLIENT_ID, GH_CLIENT_SECRET, BLOCKCYPHER_API_KEY

from users.models import AuthUser, LoggedLogin, GithubProfile

from users.forms import LoginForm, RegistrationForm, CoinSymbolForm, BCYFaucetForm

from blockcypher.utils import btc_to_satoshis
from blockcypher.api import list_forwarding_addresses, generate_new_address, send_bcy_faucet
from blockcypher.constants import COIN_CHOICES

from utils import uri_to_url

import requests
import json
from urllib.parse import parse_qs, urlencode


def github_login(request):
    params = urlencode({
        'client_id': GH_CLIENT_ID,
        'scope': 'user:email',
        'redirect_uri': uri_to_url(reverse_lazy('github_authorized')),
        # TODO: add CSRF `state` tag for added security https://developer.github.com/v3/oauth/#parameters
        })
    url = 'https://github.com/login/oauth/authorize?%s'
    return HttpResponseRedirect(url % params)


def github_authorized(request):
    auth_code = request.GET.get('code')

    TOKEN_URL = 'https://github.com/login/oauth/access_token'

    params = {
            'client_id': GH_CLIENT_ID,
            'client_secret': GH_CLIENT_SECRET,
            'code': auth_code,
            }

    r_token = requests.post(TOKEN_URL, params)

    token = parse_qs(r_token.text).get('access_token')

    # Get the github user data
    USER_URL = 'https://api.github.com/user'
    params = {'access_token': token}
    r_user = requests.get(USER_URL, params=params)
    gh_info = json.loads(r_user.text)

    # See if user already exists
    gh_profile = get_object_or_None(GithubProfile, github_id=gh_info['id'])
    if gh_profile:
        # Fetch their auth_user
        auth_user = gh_profile.authuser
    else:
        # Fetch the email (lame previous call doesn't return that info)
        EMAIL_URL = 'https://api.github.com/user/emails'
        r_email = requests.get(EMAIL_URL, params=params)
        primary_email = ''
        for email_dict in json.loads(r_email.text):
            if email_dict['primary']:
                primary_email = email_dict['email']

        # Create the github profile
        gh_profile = GithubProfile.objects.create(
                github_id=gh_info['id'],
                github_created_at=gh_info['created_at'],  # convert to DT?
                github_updated_at=gh_info['updated_at'],  # convert to DT?
                github_username=gh_info['login'],
                primary_email=primary_email,
                full_name=gh_info.get('name'),
                followers_cnt=gh_info.get('followers'),
                following_cnt=gh_info.get('following'),
                public_repo_cnt=gh_info.get('public_repos'),
                public_gists_cnt=gh_info.get('public_gists'),
                )

        # Create the user and assign gh profile
        auth_user = AuthUser.objects.create_user(email=primary_email, password=None)
        auth_user.github_profile = gh_profile
        auth_user.save()

        # Assign new BC key
        auth_user.create_new_bc_token()

    # Login the user
    # http://stackoverflow.com/a/3807891/1754586
    auth_user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, auth_user)

    # Log the login
    LoggedLogin.record_login(request)

    msg = _('Login Successful')
    messages.success(request, msg)

    return HttpResponseRedirect(reverse_lazy('dashboard'))


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
                if hasattr(existing_user, 'github_profile') and existing_user.github_profile:
                    return HttpResponseRedirect(reverse_lazy('github_login'))
                else:
                    msg = _('That email already belongs to someone, please login:')
                    messages.warning(request, msg)
                    return HttpResponseRedirect(existing_user.get_login_uri())

            else:
                # create user
                user = AuthUser.objects.create_user(
                        email=email.lower(),
                        password=password,
                )

                # Assign new BC key
                user.create_new_bc_token()

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


@login_required
@render_to('dashboard.html')
def dashboard(request):
    return {
            'bc_tokens': request.user.blockcyphertoken_set.order_by('-created_at'),
            }


def logout_request(request):
    " Log a user out using Django's logout function and redirect them "
    logout(request)
    msg = _("You Are Now Logged Out")
    messages.success(request, msg)
    return HttpResponseRedirect(reverse_lazy('user_login'))


@login_required
def create_new_key(request):
    bc_token = request.user.create_new_bc_token()
    msg = _("New Key <b>%(bc_key)s</b> Added" % {'bc_key': bc_token.key})
    messages.success(request, msg, extra_tags='safe')
    return HttpResponseRedirect(reverse_lazy('dashboard'))


@render_to('forwarding_addresses.html')
def forwarding_addresses(request, coin_symbol, api_key):
    form = CoinSymbolForm(initial={'coin_symbol': coin_symbol})
    if request.method == 'POST':
        form = CoinSymbolForm(data=request.POST)
        if form.is_valid():
            kwargs = {
                    'coin_symbol': form.cleaned_data['coin_symbol'],
                    'api_key': api_key,
                    }
            redir_url = reverse_lazy('forwarding_addresses', kwargs=kwargs)
            return HttpResponseRedirect(redir_url)

    forwarding_objects = list_forwarding_addresses(
            coin_symbol=coin_symbol,
            api_key=api_key,
            )

    return {
            'coins': COIN_CHOICES,
            'coin_symbol': coin_symbol,
            'forwarding_objects': forwarding_objects,
            'form': form,
            'api_key': api_key,
            }


@render_to('bcy_faucet.html')
def bcy_faucet(request):
    form = BCYFaucetForm(initial={'btc_to_send': .054321})
    if request.method == 'POST':
        form = BCYFaucetForm(data=request.POST)
        if form.is_valid():
            btc_to_send = form.cleaned_data['btc_to_send']
            address_to_fund = form.cleaned_data['address_to_fund']
            if not address_to_fund:
                address_to_fund = generate_new_address(coin_symbol='bcy',
                        api_key=BLOCKCYPHER_API_KEY)['address']

            tx_hash = send_bcy_faucet(
                    address_to_fund=address_to_fund,
                    satoshis=btc_to_satoshis(btc_to_send),
                    api_key=BLOCKCYPHER_API_KEY,
                    )

            msg = '%s BTC sent to %s (<a href="https://live.blockcypher.com/bcy/tx/%s/">details</a>)' % (
                btc_to_send, address_to_fund, tx_hash)

            messages.success(request, msg, extra_tags='safe')

    return {
            'form': form,
            }


def fail500(request):
    raise Exception('IntentionalFail: This Was On Purpose')

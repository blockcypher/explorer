from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape

from annoying.functions import get_object_or_None
from annoying.decorators import render_to

from blockexplorer.settings import GH_CLIENT_ID, GH_CLIENT_SECRET

from users.models import AuthUser, LoggedLogin, GithubProfile

from users.forms import LoginForm, RegistrationForm

import requests
import json
from urllib.parse import parse_qs, urlencode


def github_login(request):
    params = urlencode({
        'client_id': GH_CLIENT_ID,
        'scope': 'user:email',
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
            # TODO: add CSRF `state` tag for added security https://developer.github.com/v3/oauth/#parameters
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
                full_name=gh_info['name'],
                followers_cnt=gh_info['followers'],
                following_cnt=gh_info['following'],
                public_repo_cnt=gh_info['public_repos'],
                public_gists_cnt=gh_info['public_gists'],
                )

        # Create the user and assign gh profile
        auth_user = AuthUser.objects.create_user(email=primary_email, password=None)
        auth_user.github_profile = gh_profile
        auth_user.save()

        # TODO: assign BC key

    # Login the user
    # http://stackoverflow.com/a/3807891/1754586
    auth_user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, auth_user)

    # Log the login
    LoggedLogin.record_login(request)

    msg = _('Login Succesful')
    messages.success(request, msg)

    return HttpResponseRedirect(reverse_lazy('home'))


@render_to('login.html')
def user_login(request):
    """
    Email/pass logins, github logins are processed separately via github_authorized
    """
    user = request.user
    if user.is_authenticated():
        # TODO: notification
        return HttpResponseRedirect(reverse_lazy('home'))

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user_found = get_object_or_None(AuthUser, email=email)
            if user_found:
                user = authenticate(email=email, password=password)
                if user:
                    login(request, user)
                    LoggedLogin.record_login(request)
                    if user.is_staff:
                        return HttpResponseRedirect('/admin/')
                    else:
                        post_login_url = reverse_lazy('home')  # FIXME
                        return HttpResponseRedirect(post_login_url)
                else:
                    msg = _("Sorry, that password is incorrect.")
                    messages.warning(request, msg, extra_tags='safe')
            else:
                msg = _("No account found for <b>%(email)s</b>.") % {'email': escape(email)}
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
        form = RegistrationForm(data=request.POST, AuthUser=AuthUser)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # create user
            user = AuthUser.objects.create_user(
                    email=email.lower(),
                    password=password,
            )

            # TODO: assign BC key

            # login user
            user_to_login = authenticate(email=email, password=password)
            login(request, user_to_login)

            # Log the login
            LoggedLogin.record_login(request)

            msg = _('Login Succesful')
            messages.success(request, msg)

            return HttpResponseRedirect(reverse_lazy('home'))

    elif request.method == 'GET':
        # Preseed name and/or email if passed through GET string
        email = request.GET.get('e')
        full_name = request.GET.get('name')
        if email or full_name:
            form = RegistrationForm(initial={
                'email': email,
                'full_name': full_name,
                })
    return {'form': form}


@login_required
@render_to('dashboard.html')
def dashboard(request):
    return {}


def logout_request(request):
    " Log a user out using Django's logout function and redirect them "
    logout(request)
    msg = _("You Are Now Logged Out")
    messages.success(request, msg)
    return HttpResponseRedirect(reverse_lazy('home'))

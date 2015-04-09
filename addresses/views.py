from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY, WEBHOOK_SECRET_KEY

from blockcypher.api import get_address_details, get_address_details_url, subscribe_to_address_webhook

from users.models import AuthUser, LoggedLogin
from addresses.models import AddressSubscription
from transactions.models import OnChainTransaction
from services.models import WebHook
from emails.models import SentEmail

from addresses.forms import KnownUserAddressSubscriptionForm, NewUserAddressSubscriptionForm

from utils import get_max_pages, get_user_agent, get_client_ip, uri_to_url, simple_pw_generator

import json


@assert_valid_coin_symbol
@render_to('address_overview.html')
def address_overview(request, coin_symbol, address, wallet_name=None):

    TXNS_PER_PAGE = 100

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    try:
        address_details = get_address_details(
                address=address,
                coin_symbol=coin_symbol,
                txn_limit=5000,
                api_key=BLOCKCYPHER_API_KEY,
                )
    except AssertionError:
        msg = _('Invalid Address')
        messages.warning(request, msg)
        redir_url = reverse('coin_overview', kwargs={'coin_symbol': coin_symbol})
        return HttpResponseRedirect(redir_url)

    #import pprint; pprint.pprint(address_details, width=1)

    if 'error' in address_details:
        msg = _('Sorry, that address was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    all_transactions = address_details.get('unconfirmed_txrefs', []) + address_details.get('txrefs', [])

    # doesn't cover pagination
    confirmed_sent_satoshis, confirmed_received_satoshis = 0, 0
    unconfirmed_sent_satoshis, unconfirmed_received_satoshis = 0, 0
    for transaction in all_transactions:
        if transaction['tx_input_n'] >= 0:
            # It's sent
            if transaction['confirmations'] > 6:
                confirmed_sent_satoshis += transaction['value']
            else:
                unconfirmed_sent_satoshis += transaction['value']
        else:
            # It's received
            if transaction['confirmations'] > 6:
                confirmed_received_satoshis += transaction['value']
            else:
                unconfirmed_received_satoshis += transaction['value']

    # transaction pagination: 0-indexed and inclusive
    tx_start_num = (current_page - 1) * TXNS_PER_PAGE
    tx_end_num = current_page * TXNS_PER_PAGE - 1

    # filter address details for pagination. HACK!
    all_transactions = all_transactions[tx_start_num:tx_end_num]

    all_txids = set([tx['tx_hash'] for tx in all_transactions])

    return {
            'coin_symbol': coin_symbol,
            'address': address,
            'api_url': get_address_details_url(address=address, coin_symbol=coin_symbol),
            'wallet_name': wallet_name,
            'current_page': current_page,
            'max_pages': get_max_pages(num_items=address_details['final_n_tx'], items_per_page=TXNS_PER_PAGE),
            'confirmed_sent_satoshis': confirmed_sent_satoshis,
            'unconfirmed_sent_satoshis': unconfirmed_sent_satoshis,
            'total_sent_satoshis': unconfirmed_sent_satoshis + confirmed_sent_satoshis,
            'confirmed_received_satoshis': confirmed_received_satoshis,
            'unconfirmed_received_satoshis': unconfirmed_received_satoshis,
            'total_received_satoshis': unconfirmed_received_satoshis + confirmed_received_satoshis,
            'unconfirmed_balance_satoshis': address_details['unconfirmed_balance'],
            'confirmed_balance_satoshis': address_details['balance'],
            'total_balance_satoshis': address_details['final_balance'],
            'all_transactions': all_transactions,
            'num_confirmed_txns': address_details['n_tx'],
            'num_unconfirmed_txns': address_details['unconfirmed_n_tx'],
            'num_all_txns': address_details['final_n_tx'],
            'has_more': bool(len(all_txids) != address_details['final_n_tx']),
            'BLOCKCYPHER_PUBLIC_KEY': BLOCKCYPHER_PUBLIC_KEY,
            }


def subscribe_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('subscribe_address', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)


@assert_valid_coin_symbol
@render_to('subscribe_address.html')
def subscribe_address(request, coin_symbol):

    already_authenticated = request.user.is_authenticated()
    # kind of tricky because we have to deal with both logged in and new users

    initial = {'coin_symbol': coin_symbol}

    if already_authenticated:
        form = KnownUserAddressSubscriptionForm(initial=initial)
    else:
        form = NewUserAddressSubscriptionForm(initial=initial)

    if request.method == 'POST':
        if already_authenticated:
            form = KnownUserAddressSubscriptionForm(data=request.POST)
        else:
            form = NewUserAddressSubscriptionForm(data=request.POST)

        if form.is_valid():
            coin_symbol = form.cleaned_data['coin_symbol']
            coin_address = form.cleaned_data['coin_address']

            if already_authenticated:
                auth_user = request.user
            else:
                user_email = form.cleaned_data['email']
                # Check for existing user with that email
                existing_user = get_object_or_None(AuthUser, email=user_email)
                if existing_user:
                    msg = _('Please first login to this account to create a notification')
                    messages.info(request, msg)
                    return HttpResponseRedirect(existing_user.get_login_uri())

                else:
                    # Create user with unknown (random) password
                    auth_user = AuthUser.objects.create_user(
                            email=user_email,
                            password=None,  # it will create a random pw
                            creation_ip=get_client_ip(request),
                            creation_user_agent=get_user_agent(request),
                            )

                    # Login the user
                    # http://stackoverflow.com/a/3807891/1754586
                    auth_user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, auth_user)

                    # Log the login
                    LoggedLogin.record_login(request)

            existing_subscription_cnt = AddressSubscription.objects.filter(
                    auth_user=auth_user,
                    b58_address=coin_address).count()
            if existing_subscription_cnt:
                msg = _("You're already subscribed to that address. Please choose another address.")
                messages.warning(request, msg, extra_tags='safe')
            else:
                # Hit blockcypher and return subscription id
                callback_uri = reverse('address_webhook', kwargs={
                    'secret_key': WEBHOOK_SECRET_KEY,
                    # hack for rare case of two webhooks requested on same address:
                    'ignored_key': simple_pw_generator(num_chars=10),
                    })
                callback_url = uri_to_url(callback_uri)
                bcy_id = subscribe_to_address_webhook(
                        subscription_address=coin_address,
                        callback_url=callback_url,
                        coin_symbol=coin_symbol,
                        api_key=BLOCKCYPHER_API_KEY,
                        )

                address_subscription = AddressSubscription.objects.create(
                        coin_symbol=coin_symbol,
                        b58_address=coin_address,
                        auth_user=auth_user,
                        blockcypher_id=bcy_id,
                        )

                if already_authenticated and auth_user.email_verified:
                    msg = _('You will now be emailed notifications for <b>%(coin_address)s</b>' % {'coin_address': coin_address})
                    messages.success(request, msg, extra_tags='safe')
                    return HttpResponseRedirect(reverse('dashboard'))
                else:
                    address_subscription.send_welcome_email()
                    return HttpResponseRedirect(reverse('unconfirmed_email'))

    elif request.method == 'GET':
        coin_address = request.GET.get('a')
        subscriber_email = request.GET.get('e')
        if coin_address:
            initial['coin_address'] = coin_address
        if subscriber_email and not already_authenticated:
            initial['email'] = subscriber_email
        if coin_address or subscriber_email:
            if already_authenticated:
                form = KnownUserAddressSubscriptionForm(initial=initial)
            else:
                form = NewUserAddressSubscriptionForm(initial=initial)

    return {
            'form': form,
            'coin_symbol': coin_symbol,
            }


@login_required
def user_unsubscribe_address(request, address_subscription_id):
    '''
    For logged-in users to unsubscribe an address
    '''
    address_subscription = get_object_or_404(AddressSubscription, id=address_subscription_id)
    assert address_subscription.auth_user == request.user

    if address_subscription.unsubscribed_at:
        msg = _("You've already unsubscribed from this alert")
        messages.info(request, msg)
    else:
        address_subscription.unsubscribed_at = now()
        address_subscription.save()

        msg = _("You've been unsubscribed from notifications on %(b58_address)s" % {
            'b58_address': address_subscription.b58_address,
            })
        messages.info(request, msg)

    return HttpResponseRedirect(reverse('dashboard'))


def unsubscribe_address(request, unsub_code):
    '''
    1-click unsubscribe an address via email
    '''
    sent_email = get_object_or_404(SentEmail, unsub_code=unsub_code)

    auth_user = sent_email.auth_user

    # Login the user
    # http://stackoverflow.com/a/3807891/1754586
    auth_user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, auth_user)

    # Log the login
    LoggedLogin.record_login(request)

    if sent_email.unsubscribed_at:
        msg = _("You've already unsubscribed from this alert")
        messages.info(request, msg)

    else:
        address_subscription = sent_email.address_subscription
        assert address_subscription

        address_subscription.unsubscribed_at = now()
        address_subscription.save()

        msg = _("You've been unsubscribed from notifications on %(b58_address)s" % {
            'b58_address': address_subscription.b58_address,
            })
        messages.info(request, msg)

    return HttpResponseRedirect(reverse('dashboard'))


@csrf_exempt
def address_webhook(request, secret_key, ignored_key):
    '''
    Process an inbound webhook from blockcypher
    '''

    # Log webhook
    webhook = WebHook.log_webhook(request, WebHook.BLOCKCYPHER_ADDRESS_NOTIFICATION)

    assert secret_key == WEBHOOK_SECRET_KEY
    assert request.method == 'POST', 'Request has no post'

    blockcypher_id = request.META.get('HTTP_X_EVENTID')
    assert 'tx-confirmation' == request.META.get('HTTP_X_EVENTTYPE')

    payload = json.loads(request.body.decode())

    address_subscription = AddressSubscription.objects.get(blockcypher_id=blockcypher_id)

    tx_hash = payload['hash']
    num_confs = payload['confirmations']
    double_spend = payload['double_spend']
    satoshis_sent = payload['total']
    fee_in_satoshis = payload['fees']

    tx_event = get_object_or_None(
            OnChainTransaction,
            tx_hash=tx_hash,
            address_subscription=address_subscription,
            )

    if tx_event:
        tx_event.num_confs = num_confs
        tx_event.double_spend = double_spend
        tx_event.save()
    else:
        tx_event = OnChainTransaction.objects.create(
                tx_hash=tx_hash,
                address_subscription=address_subscription,
                num_confs=num_confs,
                double_spend=double_spend,
                satoshis_sent=satoshis_sent,
                fee_in_satoshis=fee_in_satoshis,
                )

    tx_event.send_email_notification()

    # Update logging
    webhook.address_subscription = address_subscription
    webhook.succeeded = True
    webhook.save()

    # Return something
    return HttpResponse("*ok*")

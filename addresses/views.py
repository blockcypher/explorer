from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY, WEBHOOK_SECRET_KEY

from blockcypher.api import get_address_details, get_address_details_url, subscribe_to_address_webhook

from users.models import AuthUser, LoggedLogin
from addresses.models import AddressSubscription
from transactions.models import TransactionEvent
from services.models import WebHook

from addresses.forms import KnownUserAddressSubscriptionForm, NewUserAddressSubscriptionForm

from utils import get_max_pages, get_user_agent, get_client_ip, uri_to_url, simple_pw_generator

import json


@assert_valid_coin_symbol
@render_to('address_overview.html')
def address_overview(request, coin_symbol, address):

    TXNS_PER_PAGE = 100

    # 1 indexed page
    current_page = request.GET.get('page')
    if current_page:
        current_page = int(current_page)
    else:
        current_page = 1

    address_details = get_address_details(
            address=address,
            coin_symbol=coin_symbol,
            txn_limit=5000,
            api_key=BLOCKCYPHER_API_KEY,
            )

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

            if already_authenticated:
                msg = _('You will now be emailed notifications for <b>%(coin_address)s</b>' % {'coin_address': coin_address})
                messages.success(request, msg, extra_tags='safe')
                # FIXME: make this page
                return HttpResponseRedirect(reverse('dashboard'))
            else:
                address_subscription.send_welcome_email()
                # FIXME: make this page
                return HttpResponseRedirect(reverse('unconfirmed_email'))

    elif request.method == 'GET':
        coin_address = request.GET.get('a')
        if coin_address:
            initial['coin_address'] = coin_address
            if already_authenticated:
                form = KnownUserAddressSubscriptionForm(initial=initial)
            else:
                form = NewUserAddressSubscriptionForm(initial=initial)

    return {
            'form': form,
            'coin_symbol': coin_symbol,
            }


@csrf_exempt
def address_webhook(request, secret_key, ignored_key):
    '''
    Process an inbound webhook from blockcypher
    '''

    # Log webhook
    webhook = WebHook.log_webhook(request, WebHook.BLOCKCYPHER_ADDRESS_NOTIFICATION)

    assert secret_key == WEBHOOK_SECRET_KEY
    assert request.method == 'POST', 'Request has no post'

    # event_type = request.META.get('HTTP_X_EVENTTYPE')
    payload = json.loads(request.body.decode())

    blockcypher_id = payload['blockcypher_id']  # FIXME
    address_subscription = AddressSubscription.objects.get(blockcypher_id=blockcypher_id)

    tx_event = TransactionEvent.objects.create(
            tx_hash=payload['hash'],
            address_subscription=address_subscription,
            conf_num=payload['confirmations'],
            double_spend=payload['double_spend'],
            )

    tx_event.send_email_notification()

    # Update logging
    webhook.succeeded = True
    webhook.save()

    # Return something
    return HttpResponse("*ok*")

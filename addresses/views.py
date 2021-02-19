from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt
from django.shortcuts import get_object_or_404

from annoying.decorators import render_to
from annoying.functions import get_object_or_None

from blockexplorer.decorators import assert_valid_coin_symbol

from blockexplorer.raven import client

from blockexplorer.settings import BLOCKCYPHER_PUBLIC_KEY, BLOCKCYPHER_API_KEY, WEBHOOK_SECRET_KEY, BASE_URL

from blockcypher.api import get_address_full, get_address_overview, subscribe_to_address_webhook, get_forwarding_address_details, unsubscribe_from_webhook
from blockcypher.constants import COIN_SYMBOL_MAPPINGS

from users.models import AuthUser, LoggedLogin
from addresses.models import AddressSubscription, AddressForwarding
from transactions.models import OnChainTransaction
from services.models import WebHook
from emails.models import SentEmail

from addresses.forms import KnownUserAddressSubscriptionForm, NewUserAddressSubscriptionForm, AddressSearchForm, KnownUserAddressForwardingForm, NewUserAddressForwardingForm

from utils import get_user_agent, get_client_ip, uri_to_url, simple_pw_generator

import json

from urllib.parse import urlencode

from datetime import timedelta

SMALL_PAYMENTS_MSG = '''
Please note that for very small payments of 100 bits or less,
the payment will not forward as the amount to forward is lower than the mining fee.
'''

# http://www.useragentstring.com/pages/Crawlerlist/
BOT_LIST = (
        'googlebot',
        'bingbot',
        'baiduspider',
        'yandexbot',
        'omniexplorer_bot',
        )


def is_bot(user_agent):
    if user_agent:
        user_agent_lc = user_agent.lower()
        for bot_string in BOT_LIST:
            if bot_string in user_agent_lc:
                return True
    return False


@assert_valid_coin_symbol
@render_to('address_overview.html')
def address_overview(request, coin_symbol, address, wallet_name=None):
    TXNS_PER_PAGE = 10

    if request.GET.get('page'):
        # get rid of old pagination (for googlebot)
        kwargs = {'coin_symbol': coin_symbol, 'address': address}
        return HttpResponseRedirect(reverse('address_overview', kwargs=kwargs))

    before_bh = request.GET.get('before')

    try:
        user_agent = request.META.get('HTTP_USER_AGENT')

        if is_bot(user_agent):
            # very crude hack!
            confirmations = 1
        else:
            confirmations = 0

        address_details = get_address_full(
                address=address,
                coin_symbol=coin_symbol,
                txn_limit=TXNS_PER_PAGE,
                inout_limit=5,
                confirmations=confirmations,
                api_key=BLOCKCYPHER_API_KEY,
                before_bh=before_bh,
                )
    except AssertionError:
        msg = _('Invalid Address')
        messages.warning(request, msg)
        redir_url = reverse('coin_overview', kwargs={'coin_symbol': coin_symbol})
        return HttpResponseRedirect(redir_url)

    # import pprint; pprint.pprint(address_details, width=1)

    if 'error' in address_details:
        msg = _('Sorry, that address was not found')
        messages.warning(request, msg)
        return HttpResponseRedirect(reverse('home'))

    if request.user.is_authenticated:
        # notify user on page of any forwarding or subscriptions they may have
        for address_subscription in AddressSubscription.objects.filter(
                auth_user=request.user,
                b58_address=address,
                coin_symbol=coin_symbol,
                unsubscribed_at=None,
                ):
            if address_subscription.auth_user.email_verified:
                msg = _('Private Message: you are subscribed to this address and will receive email notifications at <b>%(user_email)s</b> (<a href="%(unsub_url)s">unsubscribe</a>)' % {
                    'user_email': request.user.email,
                    'unsub_url': reverse('user_unsubscribe_address', kwargs={
                        'address_subscription_id': address_subscription.id,
                        }),
                    })
                messages.info(request, msg, extra_tags='safe')
            else:
                msg = _('Private Message: you are not subscribed to this address because you have not clicked the link sent to <b>%(user_email)s</b>' % {
                    'user_email': request.user.email,
                    })
                messages.error(request, msg, extra_tags='safe')
                print('ERROR')

        # there can be only one
        af_initial = get_object_or_None(AddressForwarding,
                auth_user=request.user,
                initial_address=address,
                coin_symbol=coin_symbol,
                )
        if af_initial:
            msg = _('''
            Private Message: this address will automatically forward to <a href="%(destination_addr_uri)s">%(destination_address)s</a>
            any time a payment is received.
            <br /><br /> <i>%(small_payments_msg)s</i>
            ''' % {
                'destination_address': af_initial.destination_address,
                'destination_addr_uri': reverse('address_overview', kwargs={
                    'address': af_initial.destination_address,
                    'coin_symbol': coin_symbol,
                    }),
                'small_payments_msg': SMALL_PAYMENTS_MSG,
                })
            messages.info(request, msg, extra_tags='safe')

        # There could be many
        for af_destination in AddressForwarding.objects.filter(
                auth_user=request.user,
                destination_address=address,
                coin_symbol=coin_symbol,
                ):
            msg = _('''
            Private Message: this address will automatically receive forwarded transactions from
            <a href="%(initial_addr_uri)s">%(initial_address)s</a>.
            <br /><br /> <i>%(small_payments_msg)s</i>
            ''' % {
                'initial_address': af_destination.initial_address,
                'initial_addr_uri': reverse('address_overview', kwargs={
                    'address': af_destination.initial_address,
                    'coin_symbol': coin_symbol,
                    }),
                'small_payments_msg': SMALL_PAYMENTS_MSG,
                })
            messages.info(request, msg, extra_tags='safe')

    all_transactions = address_details.get('txs', [])
    # import pprint; pprint.pprint(all_transactions, width=1)

    api_url = 'https://api.blockcypher.com/v1/%s/%s/addrs/%s/full?limit=50' % (
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_code'],
            COIN_SYMBOL_MAPPINGS[coin_symbol]['blockcypher_network'],
            address)

    return {
            'coin_symbol': coin_symbol,
            'address': address,
            'api_url': api_url,
            'wallet_name': wallet_name,
            'has_more': address_details.get('hasMore', False),
            'total_sent_satoshis': address_details['total_sent'],
            'total_received_satoshis': address_details['total_received'],
            'unconfirmed_balance_satoshis': address_details['unconfirmed_balance'],
            'confirmed_balance_satoshis': address_details['balance'],
            'total_balance_satoshis': address_details['final_balance'],
            'flattened_txs': all_transactions,
            'before_bh': before_bh,
            'num_confirmed_txns': address_details['n_tx'],
            'num_unconfirmed_txns': address_details['unconfirmed_n_tx'],
            'num_all_txns': address_details['final_n_tx'],
            'BLOCKCYPHER_PUBLIC_KEY': BLOCKCYPHER_PUBLIC_KEY,
            }


def subscribe_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('subscribe_address', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)


@assert_valid_coin_symbol
@render_to('subscribe_address.html')
def subscribe_address(request, coin_symbol):

    already_authenticated = request.user.is_authenticated
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
                    b58_address=coin_address,
                    unsubscribed_at=None,
                    disabled_at=None,
                    ).count()
            if existing_subscription_cnt:
                msg = _("You're already subscribed to that address. Please choose another address.")
                messages.warning(request, msg)
            else:
                # TODO: this is inefficiently happening before email verification

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

                address_uri = reverse('address_overview', kwargs={
                    'coin_symbol': coin_symbol,
                    'address': coin_address,
                    })
                if already_authenticated and auth_user.email_verified:
                    msg = _('You will now be emailed notifications for <a href="%(address_uri)s">%(coin_address)s</a>' % {
                        'coin_address': coin_address,
                        'address_uri': address_uri,
                        })
                    messages.success(request, msg, extra_tags='safe')
                    return HttpResponseRedirect(reverse('dashboard'))
                else:
                    address_subscription.send_notifications_welcome_email()
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
            'is_input_page': True,
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
        address_subscription.user_unsubscribe_subscription()

        address_uri = reverse('address_overview', kwargs={
            'coin_symbol': address_subscription.coin_symbol,
            'address': address_subscription.b58_address,
            })
        msg = _('You have been unsubscribed from notifications on <a href="%(address_uri)s">%(b58_address)s</a>' % {
            'b58_address': address_subscription.b58_address,
            'address_uri': address_uri,
            })
        messages.success(request, msg, extra_tags='safe')

    return HttpResponseRedirect(reverse('dashboard'))


@login_required
def user_archive_forwarding_address(request, address_forwarding_id):
    '''
    For logged-in users to archive a forwarding address

    For security, the address forwarding is never disabled and can't be changed.
    We just stop displaying it in the UI.
    For now we don't automatically stop sending email notices, though we may want to do that in the future.
    '''
    address_forwarding = get_object_or_404(AddressForwarding, id=address_forwarding_id)
    assert address_forwarding.auth_user == request.user

    if address_forwarding.archived_at:
        msg = _("You've already archived this address")
        messages.info(request, msg)
    else:
        address_forwarding.archived_at = now()
        address_forwarding.save()

        initial_addr_uri = reverse('address_overview', kwargs={
            'coin_symbol': address_forwarding.coin_symbol,
            'address': address_forwarding.initial_address,
            })
        destination_addr_uri = reverse('address_overview', kwargs={
            'coin_symbol': address_forwarding.coin_symbol,
            'address': address_forwarding.destination_address,
            })
        msg = _('''
        You have archived the forwarding address <a href="%(initial_addr_uri)s">%(initial_address)s</a>.
        For security, payments sent to <a href="%(destination_addr_uri)s">%(destination_address)s</a>
        may continue to forward to <a href="%(initial_addr_uri)s">%(initial_address)s</a>.
        ''' % {
            'initial_address': address_forwarding.initial_address,
            'destination_address': address_forwarding.destination_address,
            'initial_addr_uri': initial_addr_uri,
            'destination_addr_uri': destination_addr_uri,
            })
        messages.success(request, msg, extra_tags='safe')

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

        address_subscription.user_unsubscribe_subscription()

        addr_uri = reverse('address_overview', kwargs={
            'coin_symbol': address_subscription.coin_symbol,
            'address': address_subscription.b58_address,
            })

        msg = _('You have been unsubscribed from notifications on <a href="%(addr_uri)s">%(b58_address)s</a>' % {
            'b58_address': address_subscription.b58_address,
            'addr_uri': addr_uri,
            })
        messages.info(request, msg, extra_tags='safe')

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
        tx_is_new = False
        tx_event.num_confs = num_confs
        tx_event.double_spend = double_spend
        tx_event.save()
    else:
        tx_is_new = True

        input_addresses = set()
        for input_entry in payload['inputs']:
            for address in input_entry.get('addresses', []):
                input_addresses.add(address)
        if address_subscription.b58_address in input_addresses:
            is_withdrawal = True
        else:
            is_withdrawal = False

        output_addresses = set()
        for output_entry in payload.get('outputs', []):
            for address in output_entry['addresses']:
                output_addresses.add(address)
        if address_subscription.b58_address in output_addresses:
            is_deposit = True
        else:
            is_deposit = False

        tx_event = OnChainTransaction.objects.create(
                tx_hash=tx_hash,
                address_subscription=address_subscription,
                num_confs=num_confs,
                double_spend=double_spend,
                satoshis_sent=satoshis_sent,
                fee_in_satoshis=fee_in_satoshis,
                is_deposit=is_deposit,
                is_withdrawal=is_withdrawal,
                )

    # email sending logic
    # TODO: add logic for notify on deposit vs withdrawal
    # TODO: add safety check to prevent duplicate email sending
    if tx_event.address_subscription.unsubscribed_at or tx_event.address_subscription.disabled_at:
        # unsubscribe from webhooks going forward
        try:
            unsub_result = unsubscribe_from_webhook(
                    webhook_id=tx_event.address_subscription.blockcypher_id,
                    api_key=BLOCKCYPHER_API_KEY,
                    coin_symbol=tx_event.address_subscription.coin_symbol,
                    )
            assert unsub_result is True, unsub_result
        except Exception:
            # there was a problem unsubscribing
            # notify using sentry but still return the webhook to blockcypher
            client.captureException()

    elif tx_event.address_subscription.auth_user.email_verified:
        # make sure we haven't contacted too many times (and unsub if so)

        earliest_dt = now() - timedelta(days=3)
        recent_emails_sent = SentEmail.objects.filter(
                address_subscription=tx_event.address_subscription,
                sent_at__gt=earliest_dt,
                ).count()

        if recent_emails_sent > 100:
            # too many emails, unsubscribe
            tx_event.address_subscription.admin_unsubscribe_subscription()
            client.captureMessage('TX Event %s unsubscribed' % tx_event.id)
            # TODO: notify user they've been unsubscribed

        else:
            # proceed with normal email sending

            if double_spend and (tx_is_new or not tx_event.double_spend):
                # We have the first reporting of a double-spend
                tx_event.send_double_spend_tx_notification()

            elif num_confs == 0 and tx_is_new:
                # First broadcast
                if tx_event.address_subscription.notify_on_broadcast:
                    if tx_event.is_deposit and tx_event.address_subscription.notify_on_deposit:
                        tx_event.send_unconfirmed_tx_email()
                    elif tx_event.is_withdrawal and tx_event.address_subscription.notify_on_withdrawal:
                        tx_event.send_unconfirmed_tx_email()

            elif num_confs == 6:
                # Sixth confirm
                if tx_event.address_subscription.notify_on_sixth_confirm:
                    if tx_event.is_deposit and tx_event.address_subscription.notify_on_deposit:
                        tx_event.send_confirmed_tx_email()
                    elif tx_event.is_withdrawal and tx_event.address_subscription.notify_on_withdrawal:
                        tx_event.send_confirmed_tx_email()
    else:
        # active subscription with unverfied email (can't contact)
        # TODO: add unsub if orig subscription is > X days old
        # eventually these could pile up
        pass

    # Update logging
    webhook.address_subscription = address_subscription
    webhook.succeeded = True
    webhook.save()

    # Return something
    return HttpResponse("*ok*")


@xframe_options_exempt
@render_to('balance_widget.html')
def render_balance_widget(request, coin_symbol, address):
    address_overview = get_address_overview(address=address,
            coin_symbol=coin_symbol, api_key=BLOCKCYPHER_API_KEY)
    return {
            'address_overview': address_overview,
            'coin_symbol': coin_symbol,
            'b58_address': address,
            'BASE_URL': BASE_URL,
            }


@xframe_options_exempt
@render_to('received_widget.html')
def render_received_widget(request, coin_symbol, address):
    address_overview = get_address_overview(address=address,
            coin_symbol=coin_symbol, api_key=BLOCKCYPHER_API_KEY)
    return {
            'address_overview': address_overview,
            'coin_symbol': coin_symbol,
            'b58_address': address,
            'BASE_URL': BASE_URL,
            }


@render_to('search_widgets.html')
def search_widgets(request, coin_symbol):
    form = AddressSearchForm()
    if request.method == 'POST':
        form = AddressSearchForm(data=request.POST)
        if form.is_valid():
            kwargs = {
                    'coin_symbol': form.cleaned_data['coin_symbol'],
                    'address': form.cleaned_data['coin_address'],
                    }
            redir_url = reverse('widgets_overview', kwargs=kwargs)
            return HttpResponseRedirect(redir_url)
    elif request.method == 'GET':
        new_coin_symbol = request.GET.get('c')
        if new_coin_symbol:
            initial = {'coin_symbol': new_coin_symbol}
            form = AddressSearchForm(initial=initial)

    return {
            'form': form,
            'coin_symbol': coin_symbol,
            'is_input_page': True,
            }


@render_to('widgets.html')
def widgets_overview(request, coin_symbol, address):
    return {
            'coin_symbol': coin_symbol,
            'b58_address': address,
            'BASE_URL': BASE_URL,
            }


def widget_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('search_widgets', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)


@assert_valid_coin_symbol
@render_to('setup_address_forwarding.html')
def setup_address_forwarding(request, coin_symbol):

    # kind of tricky because we have to deal with both logged in and new users
    already_authenticated = request.user.is_authenticated

    initial = {'coin_symbol': coin_symbol}

    if already_authenticated:
        form = KnownUserAddressForwardingForm(initial=initial)
    else:
        form = NewUserAddressForwardingForm(initial=initial)

    if request.method == 'POST':
        if already_authenticated:
            form = KnownUserAddressForwardingForm(data=request.POST)
        else:
            form = NewUserAddressForwardingForm(data=request.POST)

        if form.is_valid():
            coin_symbol = form.cleaned_data['coin_symbol']
            destination_address = form.cleaned_data['coin_address']
            user_email = form.cleaned_data.get('email')
            # optional. null in case of KnownUserAddressForwardingForm

            if already_authenticated:
                auth_user = request.user
            else:
                auth_user = None

                if user_email:
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
                else:
                    # No user email given, proceed anonymously
                    # FIXME: confirm this
                    pass

            # Setup Payment Forwarding
            forwarding_address_details = get_forwarding_address_details(
                    destination_address=destination_address,
                    api_key=BLOCKCYPHER_API_KEY,
                    callback_url=None,  # notifications happen separately (and not always)
                    coin_symbol=coin_symbol,
                    )

            if 'error' in forwarding_address_details:
                # Display error message back to user
                messages.warning(request, forwarding_address_details['error'], extra_tags='safe')

            else:

                initial_address = forwarding_address_details['input_address']

                # create forwarding object
                address_forwarding_obj = AddressForwarding.objects.create(
                        coin_symbol=coin_symbol,
                        initial_address=initial_address,
                        destination_address=destination_address,
                        auth_user=auth_user,
                        blockcypher_id=forwarding_address_details['id'],
                        )

                subscribe_uri = reverse('subscribe_address', kwargs={'coin_symbol': coin_symbol})
                uri_qs = {'a': initial_address}
                if user_email:
                    uri_qs['e'] = user_email
                if already_authenticated:
                    uri_qs['e'] = auth_user.email
                subscribe_uri = '%s?%s' % (subscribe_uri, urlencode(uri_qs))

                initial_addr_uri = reverse('address_overview', kwargs={
                    'coin_symbol': coin_symbol,
                    'address': initial_address,
                    })
                destination_addr_uri = reverse('address_overview', kwargs={
                    'coin_symbol': coin_symbol,
                    'address': destination_address,
                    })
                msg_merge_dict = {
                        'initial_address': initial_address,
                        'initial_addr_uri': initial_addr_uri,
                        'destination_address': destination_address,
                        'destination_addr_uri': destination_addr_uri,
                        'subscribe_uri': subscribe_uri,
                        'small_payments_msg': SMALL_PAYMENTS_MSG,
                        }
                if auth_user:
                    msg_merge_dict['user_email'] = auth_user.email

                if user_email or (already_authenticated and form.cleaned_data['wants_email_notification']):

                    # Create an address subscription for all of these cases

                    # Hit blockcypher and return subscription id
                    callback_uri = reverse('address_webhook', kwargs={
                        'secret_key': WEBHOOK_SECRET_KEY,
                        # hack for rare case of two webhooks requested on same address:
                        'ignored_key': simple_pw_generator(num_chars=10),
                        })
                    callback_url = uri_to_url(callback_uri)
                    bcy_id = subscribe_to_address_webhook(
                            subscription_address=initial_address,
                            callback_url=callback_url,
                            coin_symbol=coin_symbol,
                            api_key=BLOCKCYPHER_API_KEY,
                            )

                    # only notify for deposits
                    AddressSubscription.objects.create(
                            coin_symbol=coin_symbol,
                            b58_address=initial_address,
                            auth_user=auth_user,
                            blockcypher_id=bcy_id,
                            notify_on_deposit=True,
                            notify_on_withdrawal=False,
                            address_forwarding_obj=address_forwarding_obj,
                            )

                    if user_email:
                        # New signup
                        msg = _('''
                        Transactions sent to <a href="%(initial_addr_uri)s">%(initial_address)s</a>
                        will now be automatically forwarded to <a href="%(destination_addr_uri)s">%(destination_address)s</a>,
                        but you must confirm your email to receive notifications.
                        <br /><br /> <i>%(small_payments_msg)s</i>
                        ''' % msg_merge_dict)
                        messages.success(request, msg, extra_tags='safe')

                        address_forwarding_obj.send_forwarding_welcome_email()
                        return HttpResponseRedirect(reverse('unconfirmed_email'))
                    else:
                        if auth_user.email_verified:

                            msg = _('''
                            Transactions sent to <a href="%(initial_addr_uri)s">%(initial_address)s</a>
                            will now be automatically forwarded to <a href="%(destination_addr_uri)s">%(destination_address)s</a>,
                            and you will immediately receive an email notification at <b>%(user_email)s</b>.
                            <br /><br /> <i>%(small_payments_msg)s</i>
                            ''' % msg_merge_dict)
                            messages.success(request, msg, extra_tags='safe')

                            return HttpResponseRedirect(reverse('dashboard'))

                        else:
                            # existing unconfirmed user
                            msg = _('''
                            Transactions sent to <a href="%(initial_addr_uri)s">%(initial_address)s</a>
                            will now be automatically forwarded to <a href="%(destination_addr_uri)s">%(destination_address)s</a>,
                            but you must confirm your email to receive notifications.
                            <br /><br /> <i>%(small_payments_msg)s</i>
                            ''' % msg_merge_dict)
                            messages.success(request, msg, extra_tags='safe')

                            address_forwarding_obj.send_forwarding_welcome_email()

                            return HttpResponseRedirect(reverse('unconfirmed_email'))

                elif already_authenticated:
                    # already authenticated and doesn't want subscriptions
                    msg = _('''
                    Transactions sent to <a href="%(initial_addr_uri)s">%(initial_address)s</a>
                    will now be automatically forwarded to <a href="%(destination_addr_uri)s">%(destination_address)s</a>.
                    You will not receive email notifications (<a href="%(subscribe_uri)s">subscribe</a>).
                    <br /><br /> <i>%(small_payments_msg)s</i>
                    ''' % msg_merge_dict)
                    messages.success(request, msg, extra_tags='safe')

                    return HttpResponseRedirect(reverse('dashboard'))

                else:
                    # New signup sans email
                    msg = _('''
                    Transactions sent to <a href="%(initial_addr_uri)s">%(initial_address)s</a>
                    will now be automatically forwarded to <a href="%(destination_addr_uri)s">%(destination_address)s</a>.
                    You will not receive email notifications (<a href="%(subscribe_uri)s">subscribe</a>).
                    <br /><br /> <i>%(small_payments_msg)s</i>
                    ''' % msg_merge_dict)
                    messages.success(request, msg, extra_tags='safe')

                    return HttpResponseRedirect(destination_addr_uri)

    elif request.method == 'GET':
        coin_address = request.GET.get('a')
        subscriber_email = request.GET.get('e')
        if coin_address:
            initial['coin_address'] = coin_address
        if subscriber_email and not already_authenticated:
            initial['email'] = subscriber_email
        if coin_address or subscriber_email:
            if already_authenticated:
                form = KnownUserAddressForwardingForm(initial=initial)
            else:
                form = NewUserAddressForwardingForm(initial=initial)

    return {
            'form': form,
            'coin_symbol': coin_symbol,
            'is_input_page': True,
            }


def forward_forwarding(request):
    kwargs = {'coin_symbol': 'btc'}
    redir_url = reverse('setup_address_forwarding', kwargs=kwargs)
    return HttpResponseRedirect(redir_url)

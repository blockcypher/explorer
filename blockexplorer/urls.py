from django.conf.urls import url

from addresses import views as addresses_views
from blocks import views as blocks_views
from homepage import views as homepage_views
from transactions import views as transactions_views
from users import views as users_views
from wallets import views as wallets_views



urlpatterns = [
    # Logging Test
    url(r'^fail500/$', homepage_views.fail500, name='fail500'),

    # Login
    url(r'^signuup/?$', users_views.signup, name='signup'),
    url(r'^logiin/?$', users_views.user_login, name='user_login'),
    url(r'^logout/?$', users_views.logout_request, name='logout_request'),
    url(r'^confirm/(?P<verif_code>[-\w]+)/$', users_views.confirm_subscription, name='confirm_subscription'),
    url(r'^unconfirmed-email/?$', users_views.unconfirmed_email, name='unconfirmed_email'),
    url(r'^confirm-pw-reset/(?P<email_address>[-\w@.+]+)?$', users_views.confirm_pw_reset, name='confirm_pw_reset'),
    url(r'^set-password/?$', users_views.password_upsell, name='password_upsell'),
    url(r'^change-password/?$', users_views.change_password, name='change_password'),
    url(r'^forgot-password/?$', users_views.forgot_password, name='forgot_password'),
    url(r'^reset-pw/(?P<verif_code>[-\w@.+]+)?$', users_views.reset_pw, name='reset_pw'),
    url(r'^dashboard/?$', users_views.dashboard, name='dashboard'),

    # App pages
    url(r'^$', homepage_views.home, name='home'),
    url(r'^(?P<coin_symbol>[-\w]+)/address/(?P<address>[-\w]+)/$', addresses_views.address_overview, name='address_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/address/(?P<address>[-\w]+)/(?P<wallet_name>[-\w\.]+)/$', addresses_views.address_overview, name='address_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/tx/(?P<tx_hash>[-\w]+)/$', transactions_views.transaction_overview, name='transaction_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/block/(?P<block_representation>[-\w]+)/$', blocks_views.block_overview, name='block_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/xpub/(?P<pubkey>[-\w]+)/$', wallets_views.wallet_overview, name='wallet_overview_default'),
    url(r'^(?P<coin_symbol>[-\w]+)/pushtx/$', transactions_views.push_tx, name='push_tx'),
    url(r'^(?P<coin_symbol>[-\w]+)/decodetx/$', transactions_views.decode_tx, name='decode_tx'),
    url(r'^highlights/$', homepage_views.highlights, name='highlights'),
    # AJAX calls
    url(r'^(?P<coin_symbol>[-\w]+)/tx-confidence/(?P<tx_hash>[-\w]+)/$', transactions_views.poll_confidence, name='poll_confidence'),

    # Widget
    url(r'^widgets/(?P<coin_symbol>[-\w]+)/?$', addresses_views.search_widgets, name='search_widgets'),
    url(r'^show-widgets/(?P<coin_symbol>[-\w]+)/(?P<address>[-\w]+)/$', addresses_views.widgets_overview, name='widgets_overview'),
    url(r'^widget/(?P<coin_symbol>[-\w]+)/(?P<address>[-\w]+)/balance/$', addresses_views.render_balance_widget, name='render_balance_widget'),
    url(r'^widget/(?P<coin_symbol>[-\w]+)/(?P<address>[-\w]+)/received/$', addresses_views.render_received_widget, name='render_received_widget'),

    # Forwarding Pages (URL hacks)
    url(r'^widgets/$', addresses_views.widget_forwarding, name='widget_forwarding'),
    url(r'^pushtx/$', transactions_views.pushtx_forwarding, name='pushtx_forwarding'),
    url(r'^decodetx/$', transactions_views.decodetx_forwarding, name='decodetx_forwarding'),
    url(r'^latest-block/$', blocks_views.latest_block_forwarding, name='latest_block_forwarding'),
    url(r'^(?P<coin_symbol>[-\w]+)/latest-block/$', blocks_views.latest_block, name='latest_block'),
    url(r'^latest-unconfirmed-tx/$', transactions_views.latest_unconfirmed_tx_forwarding, name='latest_unconfirmed_tx_forwarding'),
    url(r'^(?P<coin_symbol>[-\w]+)/latest-unconfirmed-tx/$', transactions_views.latest_unconfirmed_tx, name='latest_unconfirmed_tx'),
    url(r'^(?P<coin_symbol>[-\w]+)/block/(?P<block_num>[\d]+)/(?P<tx_num>[\d]+)/$', blocks_views.block_ordered_tx, name='block_ordered_tx'),

    # So broad it must be last
    url(r'^(?P<coin_symbol>[-\w]+)/$', homepage_views.coin_overview, name='coin_overview')
]


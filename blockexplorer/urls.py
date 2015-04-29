from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    # Logging Test
    url(r'^fail500/$', 'homepage.views.fail500', name='fail500'),

    # Login
    url(r'^signup/?$', 'users.views.signup', name='signup'),
    url(r'^login/?$', 'users.views.user_login', name='user_login'),
    url(r'^logout/?$', 'users.views.logout_request', name='logout_request'),
    url(r'^confirm/(?P<verif_code>[-\w]+)/$', 'users.views.confirm_subscription', name='confirm_subscription'),
    url(r'^unconfirmed-email/?$', 'users.views.unconfirmed_email', name='unconfirmed_email'),
    url(r'^confirm-pw-reset/(?P<email_address>[-\w@.+]+)?$', 'users.views.confirm_pw_reset', name='confirm_pw_reset'),
    url(r'^set-password/?$', 'users.views.password_upsell', name='password_upsell'),
    url(r'^change-password/?$', 'users.views.change_password', name='change_password'),
    url(r'^forgot-password/?$', 'users.views.forgot_password', name='forgot_password'),
    url(r'^reset-pw/(?P<verif_code>[-\w@.+]+)?$', 'users.views.reset_pw', name='reset_pw'),
    url(r'^unsubscribe/(?P<unsub_code>[-\w]+)/$', 'addresses.views.unsubscribe_address', name='unsubscribe_address'),
    url(r'^remove-subscription/(?P<address_subscription_id>[-\w]+)/$', 'addresses.views.user_unsubscribe_address', name='user_unsubscribe_address'),
    url(r'^archive-forwarding-address/(?P<address_forwarding_id>[-\w]+)/$', 'addresses.views.user_archive_forwarding_address', name='user_archive_forwarding_address'),
    url(r'^dashboard/?$', 'users.views.dashboard', name='dashboard'),

    # Webhooks:
    url(r'^address-webhook/(?P<secret_key>[-\w]+)/(?P<ignored_key>[-\w]+)?$', 'addresses.views.address_webhook', name='address_webhook'),

    # Admin
    url(r'^admin/', include(admin.site.urls)),

    # App pages
    url(r'^$', 'homepage.views.home', name='home'),
    url(r'^(?P<coin_symbol>[-\w]+)/forwarding/$', 'addresses.views.setup_address_forwarding', name='setup_address_forwarding'),
    url(r'^(?P<coin_symbol>[-\w]+)/subscribe/$', 'addresses.views.subscribe_address', name='subscribe_address'),
    url(r'^(?P<coin_symbol>[-\w]+)/address/(?P<address>[-\w]+)/$', 'addresses.views.address_overview', name='address_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/address/(?P<address>[-\w]+)/(?P<wallet_name>[-\w\.]+)/$', 'addresses.views.address_overview', name='address_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/tx/(?P<tx_hash>[-\w]+)/$', 'transactions.views.transaction_overview', name='transaction_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/tx-confidence/(?P<tx_hash>[-\w]+)/$', 'transactions.views.poll_confidence', name='poll_confidence'),
    url(r'^(?P<coin_symbol>[-\w]+)/block/(?P<block_representation>[-\w]+)/$', 'blocks.views.block_overview', name='block_overview'),
    url(r'^(?P<coin_symbol>[-\w]+)/pushtx/$', 'transactions.views.push_tx', name='push_tx'),
    url(r'^(?P<coin_symbol>[-\w]+)/decodetx/$', 'transactions.views.decode_tx', name='decode_tx'),
    url(r'^highlights/$', 'homepage.views.highlights', name='highlights'),

    # Widget
    url(r'^widgets/(?P<coin_symbol>[-\w]+)/?$', 'addresses.views.search_widgets', name='search_widgets'),
    url(r'^show-widgets/(?P<coin_symbol>[-\w]+)/(?P<address>[-\w]+)/$', 'addresses.views.widgets_overview', name='widgets_overview'),
    url(r'^widget/(?P<coin_symbol>[-\w]+)/(?P<address>[-\w]+)/balance/$', 'addresses.views.render_balance_widget', name='render_balance_widget'),
    url(r'^widget/(?P<coin_symbol>[-\w]+)/(?P<address>[-\w]+)/received/$', 'addresses.views.render_received_widget', name='render_received_widget'),
    url(r'^widgets/$', 'addresses.views.widget_forwarding', name='widget_forwarding'),

    # Forwarding Pages (URL hacks)
    url(r'^forwarding/$', 'addresses.views.forward_forwarding', name='forward_forwarding'),  # awesome name
    url(r'^subscribe/$', 'addresses.views.subscribe_forwarding', name='subscribe_forwarding'),
    url(r'^pushtx/$', 'transactions.views.pushtx_forwarding', name='pushtx_forwarding'),
    url(r'^decodetx/$', 'transactions.views.decodetx_forwarding', name='decodetx_forwarding'),
    url(r'^latest-block/$', 'blocks.views.latest_block_forwarding', name='latest_block_forwarding'),
    url(r'^(?P<coin_symbol>[-\w]+)/latest-block/$', 'blocks.views.latest_block', name='latest_block'),
    url(r'^latest-unconfirmed-tx/$', 'transactions.views.latest_unconfirmed_tx_forwarding', name='latest_unconfirmed_tx_forwarding'),
    url(r'^(?P<coin_symbol>[-\w]+)/latest-unconfirmed-tx/$', 'transactions.views.latest_unconfirmed_tx', name='latest_unconfirmed_tx'),

    # So broad it must be last
    url(r'^(?P<coin_symbol>[-\w]+)/$', 'homepage.views.coin_overview', name='coin_overview'),

)

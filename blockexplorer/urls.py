from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    # Logging Test
    url(r'^fail500/$', 'homepage.views.fail500', name='fail500'),

    url(r'^admin/', include(admin.site.urls)),

    # App pages
    url(r'^$', 'homepage.views.home', name='home'),
    url(r'(?P<coin_symbol>[-\w]+)/subscribe/$', 'addresses.views.subscribe_address', name='subscribe_address'),
    url(r'(?P<coin_symbol>[-\w]+)/latest-block/$', 'blocks.views.latest_block', name='latest_block'),
    url(r'(?P<coin_symbol>[-\w]+)/address/(?P<address>[-\w]+)/$', 'addresses.views.address_overview', name='address_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/tx/(?P<tx_hash>[-\w]+)/$', 'transactions.views.transaction_overview', name='transaction_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/tx-confidence/(?P<tx_hash>[-\w]+)/$', 'transactions.views.poll_confidence', name='poll_confidence'),
    url(r'(?P<coin_symbol>[-\w]+)/block/(?P<block_representation>[-\w]+)/$', 'blocks.views.block_overview', name='block_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/pushtx/$', 'transactions.views.push_tx', name='push_tx'),
    # So broad it must be last
    url(r'(?P<coin_symbol>[-\w]+)/$', 'homepage.views.coin_overview', name='coin_overview'),

    # Webhooks:

    # Process emails:
    url(r'confirm/(?P<verif_code>[-\w]+)/$', 'users.views.confirm_subscription', name='confirm_subscription'),

)

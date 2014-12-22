from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    # Logging Test
    url(r'^fail500/$', 'homepage.views.fail500', name='fail500'),

    url(r'^admin/', include(admin.site.urls)),

    # App pages
    url(r'^$', 'homepage.views.home', name='home'),
    url(r'(?P<coin_symbol>[-\w]+)/latest-block/$', 'blocks.views.latest_block', name='latest_block'),
    url(r'(?P<coin_symbol>[-\w]+)/address/(?P<address>[-\w]+)/$', 'addresses.views.address_overview', name='address_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/tx/(?P<tx_hash>[-\w]+)/$', 'transactions.views.transaction_overview', name='transaction_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/tx-confidence/(?P<tx_hash>[-\w]+)/$', 'transactions.views.poll_confidence', name='poll_confidence'),
    url(r'(?P<coin_symbol>[-\w]+)/block/(?P<block_representation>[-\w]+)/$', 'blocks.views.block_overview', name='block_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/pushtx/$', 'transactions.views.push_tx', name='push_tx'),

    # Login
    url(r'^github/authorized/', 'users.views.github_authorized', name='github_authorized'),
    url(r'^github/login/', 'users.views.github_login', name='github_login'),
    url(r'^login/', 'users.views.user_login', name='user_login'),
    url(r'^logout/?$', 'users.views.logout_request', name='logout'),
    url(r'^sign-up/', 'users.views.signup', name='signup'),

    # Profile
    url(r'^dashboard/', 'users.views.dashboard', name='dashboard'),

    # So broad it must be last (app page)
    url(r'(?P<coin_symbol>[-\w]+)/$', 'homepage.views.coin_overview', name='coin_overview'),
)

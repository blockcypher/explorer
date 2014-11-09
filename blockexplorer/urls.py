from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^$', 'homepage.views.home', name='home'),
    url(r'(?P<coin_symbol>[-\w]+)/address/(?P<address>\w+)$', 'addresses.views.address_overview', name='address_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/tx/(?P<tx_hash>\w+)$', 'transactions.views.transaction_overview', name='transaction_overview'),
    url(r'(?P<coin_symbol>[-\w]+)/block/(?P<block_representation>\w+)$', 'blocks.views.block_overview', name='block_overview'),

    url(r'^admin/', include(admin.site.urls)),
)

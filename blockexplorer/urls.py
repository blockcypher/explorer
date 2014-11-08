from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

    url(r'^$', 'homepage.views.home', name='home'),
    url(r'address/(?P<btc_address>\w+)$', 'addresses.views.address_overview', name='address_overview'),
    url(r'tx/(?P<tx_hash>\w+)$', 'transactions.views.transaction_overview', name='transaction_overview'),

    url(r'^admin/', include(admin.site.urls)),
)

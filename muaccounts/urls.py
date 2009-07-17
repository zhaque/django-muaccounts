from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'muaccounts.views.account_detail', {}, 'muaccounts_account_detail'),
    (r'^create/$', 'muaccounts.views.create_account', {}, 'muaccounts_create_account'),
    )

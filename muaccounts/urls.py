from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'muaccounts.views.account_detail', {}, 'muaccounts_account_detail'),
    (r'^changed/$', 'django.views.generic.simple.direct_to_template', dict(template='muaccounts/account_changed.html'), 'muaccounts_account_changed'),
    )

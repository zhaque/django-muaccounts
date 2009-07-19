from django.conf.urls.defaults import *

# to main site urlconf add also:
# (r'^create/$', 'muaccounts.views.create_account'),

urlpatterns = patterns('',
    (r'^$', 'muaccounts.views.account_detail', {}, 'muaccounts_account_detail'),
    (r'^remove_member/(?P<user_id>\d+)/$', 'muaccounts.views.remove_member', {}, 'muaccounts_remove_member'),
    )

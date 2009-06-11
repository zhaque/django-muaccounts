from django.conf import settings
from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.cache import patch_vary_headers

from models import MUAccount

class MUAccountsMiddleware:
    def __init__(self):
        self.default = getattr(settings, 'MUACCOUNTS_DEFAULT_DOMAIN',
                               Site.objects.get_current().domain)
        self.urlconf = getattr(settings, 'MUACCOUNTS_ACCOUNT_URLCONF', None)

    def process_request(self, request):
        host = request.META['HTTP_HOST']
        try:
            if host.endswith(MUAccount.subdomain_root):
                mua = MUAccount.objects.get(
                    domain=host[:-len(MUAccount.subdomain_root)], is_subdomain=True)
            else:
                mua = MUAccount.objects.get(domain=host, is_subdomain=False)
            request.muaccount = mua
            if self.urlconf:
                request.urlconf = self.urlconf
            if request.user.is_authenticated():
                if not mua.is_public:
                    if request.user<>mua.owner and request.user not in mua.members.all():
                        logout(request)
                        return HttpResponseRedirect(reverse('muaccounts_not_a_member', urlconf=self.urlconf))
        except MUAccount.DoesNotExist:
            if host <> self.default:
                return HttpResponseRedirect('http://%s/'%self.default)

    def process_response(self, request, response):
        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))
        return response

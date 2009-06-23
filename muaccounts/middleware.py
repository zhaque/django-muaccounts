from django.conf import settings
from django.contrib.auth import logout
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.cache import patch_vary_headers

from models import MUAccount
import signals

class MUAccountsMiddleware:
    def __init__(self):
        self.urlconf = getattr(settings, 'MUACCOUNTS_ACCOUNT_URLCONF', None)

        if hasattr(settings, 'MUACCOUNTS_PORT'):
            self.port_suffix = ':%d' % settings.MUACCOUNTS_PORT
        else: self.port_suffix = ''

        self.default_domain = getattr(settings, 'MUACCOUNTS_DEFAULT_DOMAIN', None)
        self.default_url = getattr(settings, 'MUACCOUNTS_DEFAULT_URL',
                                   'http://%s%s/' % (
                                       self.default_domain or Site.objects.get_current().domain,
                                       self.port_suffix ))

    def process_request(self, request):
        host = request.META.get('HTTP_HOST',None)
        if host is None: return # Pages CMS middleware does some evil magic in admin interface

        # strip port suffix if present
        if self.port_suffix and host.endswith(self.port_suffix):
            host = host[:-len(self.port_suffix)]

        try:
            if host.endswith(MUAccount.subdomain_root):
                mua = MUAccount.objects.get(
                    domain=host[:-len(MUAccount.subdomain_root)], is_subdomain=True)
            else:
                mua = MUAccount.objects.get(domain=host, is_subdomain=False)
        except MUAccount.DoesNotExist:
            if host <> self.default_domain:
                return HttpResponseRedirect(self.default_url)
        else:
            # set up request parameters
            request.muaccount = mua
            if self.urlconf:
                request.urlconf = self.urlconf

            # force logout of non-member and non-owner from non-public site
            if request.user.is_authenticated() and not mua.is_public \
                   and request.user <> mua.owner \
                   and request.user not in mua.members.all():
                logout(request)
                return HttpResponseRedirect(reverse('muaccounts_not_a_member', urlconf=self.urlconf))

            # call request hook
            for receiver,retval in signals.muaccount_request.send(sender=request, request=request, muaccount=mua):
                if isinstance(retval, HttpResponse):
                    return retval
            

    def process_response(self, request, response):
        if getattr(request, "urlconf", None):
            patch_vary_headers(response, ('Host',))
        return response

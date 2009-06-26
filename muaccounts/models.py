from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

import signals             # so that they get initialized early enough

def _subdomain_root():
    root = settings.MUACCOUNTS_ROOT_DOMAIN
    if not root.startswith('.'):
        root = '.'+root
    return root

class MUAccount(models.Model):
    owner = models.OneToOneField(User, help_text=_('Owner'))
    members = models.ManyToManyField(User, related_name='muaccount_member', blank=True, help_text=_('Members'))
    domain = models.CharField(max_length=256, unique=True, help_text=_('Domain'))
    is_subdomain = models.BooleanField(default=True, help_text=_('Is subdomain'))
    is_public = models.BooleanField(default=True, help_text=_('Is public'))

    subdomain_root = _subdomain_root()

    def __unicode__(self):
        return self.domain

    def get_absolute_url(self):
        if hasattr(settings, 'MUACCOUNTS_PORT'): port=':%d'%settings.MUACCOUNTS_PORT
        else: port = ''

        if self.is_subdomain:
            return 'http://%s%s%s/' % (self.domain, self.subdomain_root, port)
        else:
            return 'http://%s%s/' % (self.domain, port)

    class Meta:
        permissions = (
            ('can_set_custom_domain', 'Can set custom domain'),
            ('can_set_public_status', 'Can set public status'),
            )


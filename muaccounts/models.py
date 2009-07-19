from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import ugettext_lazy as _

import signals             # so that they get initialized early enough

from model_fields import RemovableImageField, PickledObjectField
from themes import DEFAULT_THEME_DICT

def _subdomain_root():
    root = settings.MUACCOUNTS_ROOT_DOMAIN
    if not root.startswith('.'):
        root = '.'+root
    return root

def _muaccount_logo_path(instance, filename):
    return 'muaccount-logos/%d.jpg' % instance.pk

class MUAccount(models.Model):
    owner = models.OneToOneField(User, verbose_name=_('Owner'))
    members = models.ManyToManyField(User, related_name='muaccount_member', blank=True, verbose_name=_('Members'))
    name = models.CharField(max_length=256, verbose_name=_('Name'))
    logo = RemovableImageField(upload_to=_muaccount_logo_path, null=True, blank=True)
    domain = models.CharField(max_length=256, unique=True, verbose_name=_('Domain'), blank=True, null=True)
    subdomain = models.CharField(max_length=256, unique=True, verbose_name=_('Subdomain'), null=True)
    is_public = models.BooleanField(default=True, verbose_name=_('Is public'))
    theme = PickledObjectField(default=(lambda : DEFAULT_THEME_DICT), verbose_name=_('Theme')) # lambda to work around http://code.djangoproject.com/ticket/8633

    subdomain_root = _subdomain_root()

    def __unicode__(self):
        return self.name or self.domain or self.subdomain+self.subdomain_root

    def get_full_domain(self):
        return self.domain or self.subdomain+self.subdomain_root
        return self.domain

    def get_absolute_url(self):
        if hasattr(settings, 'MUACCOUNTS_PORT'): port=':%d'%settings.MUACCOUNTS_PORT
        else: port = ''
        return 'http://%s%s/' % (self.get_full_domain(), port)

    class Meta:
        permissions = (
            ('can_set_custom_domain', 'Can set custom domain'),
            ('can_set_public_status', 'Can set public status'),
            )


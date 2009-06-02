from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

def _subdomain_root():
    if hasattr(settings,'MUACCOUNTS_ROOT_DOMAIN'):
        root = settings.MUACCOUNTS_ROOT_DOMAIN
    else:
        root = Site.objects.get_current().domain
        if root.startswith('www.'):
            root = root[4:]
    if not root.endswith('.'):
        root = '.'+root
        return root

class MUAccount(models.Model):
    owner = models.OneToOneField(User, editable=False)
    members = models.ManyToManyField(User, related_name='muaccount_member')
    domain = models.CharField(max_length=256, unique=True)
    is_subdomain = models.BooleanField(default=True)

    subdomain_root = _subdomain_root()

    def __unicode__(self):
        return self.domain

    def get_absolute_url(self):
        if self.is_subdomain:
            return 'http://%s%s/' % (self.domain, self.subdomain_root)
        else:
            return 'http://%s/' % self.domain

    class Meta:
        permissions = (
            ('can_set_custom_domain', 'Can set custom domain'),
            )


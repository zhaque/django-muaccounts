import re, socket

from django import forms
from django.conf import settings

from models import MUAccount

class MUAccountForm(forms.ModelForm):
    class Meta:
        model = MUAccount
        exclude = ('owner', 'members',)
    _domain_re = re.compile('^[a-z0-9][a-z0-9-.]+[a-z0-9]$')

    def _can_set_custom_domain(self):
        return self.instance.owner.has_perm('muaccounts.can_set_custom_domain')

    def clean_domain(self):
        d = self.cleaned_data['domain'].strip()
        if not self._domain_re.match(d):
            raise forms.ValidationError('Invalid domain name.')
        if d.endswith(MUAccount.subdomain_root):
            if not self._can_set_custom_domain():
                d = d[:-len(MUAccount.subdomain_root)]
            else:
                raise forms.ValidationError(
                    'For subdomain of %s, check the "Is subdomain" field.'
                    % MUAccount.subdomain_root)
        return d

    def clean_is_subdomain(self):
        if not self._can_set_custom_domain():
            return True
        return self.cleaned_data['is_subdomain']

    def clean_is_public(self):
        if self.instance.owner.has_perm('muaccounts.can_set_public_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public

    def clean(self):
        if self._can_set_custom_domain() and not self.cleaned_data['is_subdomain']:
            d = self.cleaned_data.get('domain',None)
            if d is None: return self.cleaned_data
            try:
                ip = socket.gethostbyname(d)
                if hasattr(settings, 'MUACCOUNTS_IP'):
                    if callable(settings.MUACCOUNTS_IP):
                        if not settings.MUACCOUNTS_IP(ip):
                            self._errors['domain'] = forms.util.ErrorList([
                                'Domain %s does not resolve to a correct IP number.' % d ])
                    else:
                        if ip <> settings.MUACCOUNTS_IP:
                            self._errors['domain'] = forms.util.ErrorList([
                                'Domain %s does not resolve to %s.' % (d, settings.MUACCOUNTS_IP) ])
            except socket.error, msg:
                self._errors['domain'] = forms.util.ErrorList([
                    'Cannot resolve domain %s: %s'%(d,msg) ])
        return self.cleaned_data

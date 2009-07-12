import re, socket

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from models import MUAccount

_muaform_exclude = ('owner', 'members',)
if not getattr(settings, 'MUACCOUNTS_THEMES', None):
    _muaform_exclude += ('theme',)

class MUAccountForm(forms.ModelForm):
    class Meta:
        model = MUAccount
        exclude = _muaform_exclude
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
                    _('For subdomain of %s, check the "Is subdomain" field.')
                    % MUAccount.subdomain_root)
        return d.lower()

    def clean_is_subdomain(self):
        if not self._can_set_custom_domain():
            return True
        return self.cleaned_data['is_subdomain']

    def clean_is_public(self):
        if self.instance.owner.has_perm('muaccounts.can_set_public_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public

    def clean(self):
        if self.cleaned_data['is_subdomain']:
            for pattern in getattr(settings, 'MUACCOUNTS_SUBDOMAIN_STOPWORDS', ('www',)):
                if re.search(pattern, self.cleaned_data['domain'], re.I):
                    self._errors['domain'] = forms.util.ErrorList([
                        _('It is not allowed to use this domain name.')])
        if self._can_set_custom_domain() and not self.cleaned_data['is_subdomain']:
            d = self.cleaned_data.get('domain',None)
            if d is None: return self.cleaned_data
            try:
                ip = socket.gethostbyname(d)
                if hasattr(settings, 'MUACCOUNTS_IP'):
                    if callable(settings.MUACCOUNTS_IP):
                        if not settings.MUACCOUNTS_IP(ip):
                            self._errors['domain'] = forms.util.ErrorList([
                                _('Domain %s does not resolve to a correct IP number.') % d ])
                    else:
                        if ip <> settings.MUACCOUNTS_IP:
                            self._errors['domain'] = forms.util.ErrorList([
                                _('Domain %(domain)s does not resolve to %(ip)s.') % {'domain':d, 'ip':settings.MUACCOUNTS_IP} ])
            except socket.error, msg:
                self._errors['domain'] = forms.util.ErrorList([
                    _('Cannot resolve domain %(domain)s: %(error_string)s')%{'domain':d,'error_string':msg} ])
        return self.cleaned_data

class AddUserForm(forms.Form):
    user = forms.CharField(label='User',
                           help_text='Enter login name or e-mail address',
                           )
    def clean_user(self):
        un = self.cleaned_data['user']
        try:
            if '@' in un: u = User.objects.get(email=un)
            else: u = User.objects.get(username=un)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User does not exist.'))
        return u

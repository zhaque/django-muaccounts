import re, socket

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.safestring import SafeUnicode
from django.utils.translation import ugettext as _

from models import MUAccount
from themes import ThemeField

class SubdomainInput(forms.TextInput):
    def render(self, *args, **kwargs):
        return SafeUnicode(
            super(SubdomainInput,self).render(*args,**kwargs)
            + MUAccount.subdomain_root )

class MUAccountCreateForm(forms.Form):
    name = forms.CharField()
    subdomain = forms.CharField(widget=SubdomainInput)

    _subdomain_re = re.compile('^[a-z0-9][a-z0-9-]+[a-z0-9]$')
    def clean_subdomain(self):
        subdomain = self.cleaned_data['subdomain'].lower().strip()

        if not self._subdomain_re.match(subdomain):
            raise forms.ValidationError(
                _('Invalid subdomain name.  You may only use a-z, 0-9, and "-".'))

        for pattern in getattr(settings, 'MUACCOUNTS_SUBDOMAIN_STOPWORDS', ('www',)):
            if re.search(pattern, subdomain, re.I):
                raise forms.ValidationError(
                    _('It is not allowed to use this domain name.'))

        try: MUAccount.objects.get(subdomain=subdomain)
        except MUAccount.DoesNotExist: pass
        else: raise forms.ValidationError(
            _('An account with this subdomain already exists.'))

        return subdomain

    def get_instance(self, user):
        if self.is_valid():
            return MUAccount.objects.create(
                owner=user,
                name=self.cleaned_data['name'],
                subdomain=self.cleaned_data['subdomain'],
                )

_muaform_exclude = ('owner', 'members', 'subdomain')
if not getattr(settings, 'MUACCOUNTS_THEMES', None):
    _muaform_exclude += ('theme',)

class MUAccountForm(forms.ModelForm):
    theme = ('theme' in _muaform_exclude) or ThemeField()
    class Meta:
        model = MUAccount
        exclude = _muaform_exclude

    _domain_re = re.compile('^[a-z0-9][a-z0-9-.]+[a-z0-9]$')
    def clean_domain(self):
        if not self.instance.owner.has_perm('muaccounts.can_set_custom_domain'):
            raise forms.ValidationError(_('You cannot set custom domain name.'))

        d = self.cleaned_data['domain'].strip()

        if not self._domain_re.match(d):
            raise forms.ValidationError('Invalid domain name.')

        if d.endswith(MUAccount.subdomain_root):
            raise forms.ValidationError(
                _('You cannot set subdomain of %s.') % MUAccount.subdomain_root)

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

        return d.lower()

    def clean_is_public(self):
        if self.instance.owner.has_perm('muaccounts.can_set_public_status'):
            return self.cleaned_data['is_public']
        return self.instance.is_public

class AddUserForm(forms.Form):
    user = forms.CharField(label='User',
                           help_text='Enter login name or e-mail address',
                           )
    def __init__(self, *args, **kwargs):
        try: self.muaccount = kwargs['muaccount']
        except KeyError: pass
        else: del kwargs['muaccount']
        super(AddUserForm, self).__init__(*args, **kwargs)

    def clean_user(self):
        un = self.cleaned_data['user']
        try:
            if '@' in un: u = User.objects.get(email=un)
            else: u = User.objects.get(username=un)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User does not exist.'))
        if u == self.muaccount.owner:
            raise forms.ValidationError(_('You are already the plan owner.'))
        return u

    def clean(self):
        try:
            limit = self.muaccount.owner.quotas.muaccount_members
        except AttributeError: pass
        else:
            if limit <= len(self.muaccount.members.all()):
                raise forms.ValidationError(_("Member limit reached."))
        return self.cleaned_data

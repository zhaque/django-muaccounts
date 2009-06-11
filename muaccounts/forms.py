import re

from django import forms

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

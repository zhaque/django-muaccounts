import re

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from forms import MUAccountForm
from models import MUAccount

def _domainify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9-]+', '-', s)
    s = re.sub(r'^-+', '', s)
    s = re.sub(r'-+$', '', s)
    return s

@login_required
def create_account(request, return_to=None):
    if return_to is None:
        return_to = reverse('muaccounts_account_detail')

    # Don't re-create account if one exists.
    try: request.user.muaccount
    except MUAccount.DoesNotExist: pass
    else: return HttpResponseRedirect(return_to)

    base_dn = _domainify(request.user.username)

    taken_domains = set([
        mua.domain for mua in MUAccount.objects.filter(
            domain__contains=base_dn).all()])

    if base_dn not in taken_domains:
        mua = MUAccount(owner=request.user, domain=base_dn)
    else:
        i = 0
        while True:
            i += 1
            dn = '%s-%d' % (base_dn, i)
            if dn not in taken_domains:
                mua = MUAccount(owner=request.user, domain=dn)
                break

    mua.save()    # race condition here, but it's only an example code
    return HttpResponseRedirect(return_to)

@login_required
def account_detail(request, return_to=None):
    account = get_object_or_404(MUAccount, owner=request.user)
    if return_to is None:
        return_to = reverse('muaccounts_account_changed')

    if request.method == 'POST':
        form = MUAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(return_to)
    else:
        form = MUAccountForm(instance=account)

    if not request.user.has_perm('muaccounts.can_set_custom_domain'):
         form.fields['is_subdomain'].widget = HiddenInput()
         # no need to change value, will be forced to True when validating.

    return direct_to_template(
        request, template='muaccounts/account_detail.html',
        extra_context=dict(object=account, form=form))

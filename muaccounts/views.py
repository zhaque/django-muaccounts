import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from forms import MUAccountCreateForm, MUAccountForm, AddUserForm
from models import MUAccount

try: import sso
except ImportError: USE_SSO = False
else: USE_SSO = getattr(settings, 'MUACCOUNTS_USE_SSO', True)
def redirect_to_muaccount(mua):
    if USE_SSO:
        return HttpResponseRedirect(
            reverse('sso')+'?next='+mua.get_absolute_url())
    else:
        return HttpResponseRedirect(mua.get_absolute_url())

@login_required
def create_account(request):
    # Don't re-create account if one exists.
    try: mua = request.user.muaccount
    except MUAccount.DoesNotExist: pass
    else: return redirect_to_muaccount(mua)

    if request.method == 'POST':
        form = MUAccountCreateForm(request.POST)
        mua = form.get_instance(request.user)
        if mua:
            return redirect_to_muaccount(mua)
    else:
        # suggest a free subdomain name based on username.
        # Domainify username: lowercase, change non-alphanumeric to
        # dash, strip leading and trailing dashes
        dn = base = re.sub(r'[^a-z0-9-]+', '-', request.user.username.lower()).strip('-')
        taken_domains = set([
            mua.domain for mua in MUAccount.objects.filter(
                domain__contains=base).all() ])
        i = 0
        while dn in taken_domains:
            i += 1
            dn = '%s-%d' % (base, i)
        form = MUAccountCreateForm({'subdomain':dn, 'name':request.user.username})
    return direct_to_template(request, 'muaccounts/create_account.html', {'form':form})

@login_required
def account_detail(request):
    # We edit current user's MUAccount
    account = get_object_or_404(MUAccount, owner=request.user)

    # but if we're inside a MUAccount, we only allow editing that muaccount.
    if getattr(request, 'muaccount', account) <> account:
        return HttpResponseForbidden()

    if 'domain' in request.POST:
        form = MUAccountForm(request.POST, request.FILES, instance=account)
        if form.is_valid():
            form.save()
    else:
        form = MUAccountForm(instance=account)

    if 'user' in request.POST:
        uform = AddUserForm(request.POST, muaccount=account)
        if uform.is_valid():
            account.members.add(uform.cleaned_data['user'])
            account.save()
    else:
        uform = AddUserForm()

    if not request.user.has_perm('muaccounts.can_set_custom_domain'):
         form.fields['domain'].widget = HiddenInput()
         # no need to change value, will be forced to True when validating.

    if not request.user.has_perm('muaccounts.can_set_public_status'):
        form.fields['is_public'].widget = HiddenInput()

    return direct_to_template(
        request, template='muaccounts/account_detail.html',
        extra_context=dict(object=account, form=form, add_user_form=uform))

@login_required
def remove_member(request, user_id):
    if request.method <> 'POST': return HttpResponseForbidden()
    # We edit current user's MUAccount
    account = get_object_or_404(MUAccount, owner=request.user)

    # but if we're inside a MUAccount, we only allow editing that muaccount.
    if getattr(request, 'muaccount', account) <> account:
        return HttpResponseForbidden()

    user = get_object_or_404(User, id=user_id)
    if user in account.members.all():
        account.members.remove(user)

    return HttpResponseRedirect(reverse('muaccounts_account_detail'))

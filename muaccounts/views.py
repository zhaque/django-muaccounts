from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms.widgets import HiddenInput
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.shortcuts import get_object_or_404

from forms import MUAccountForm
from models import MUAccount


@login_required
def account_detail(request, return_to=reverse('muaccounts_account_changed')):
    account = get_object_or_404(MUAccount, owner=request.user)

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

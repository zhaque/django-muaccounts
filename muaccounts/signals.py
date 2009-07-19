from django.dispatch import Signal

# Called by middleware on every request; If any receiver returns a
# HttpResponse instance, this instance will be returned from the
# request.
muaccount_request = Signal()

# Called by MUAccount.add_member(), provides `user' argument.
add_member = Signal()

# Called by MUAccount.remove_member(), provides `user' argument
remove_member = Signal()

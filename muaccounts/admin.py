from django.contrib import admin

from models import MUAccount

class MUAccountAdmin(admin.ModelAdmin):
    pass
admin.site.register(MUAccount, MUAccountAdmin)

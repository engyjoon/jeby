from django.contrib import admin
from .models import Keyword, Recipient, Setting, Site


admin.site.register(Keyword)
admin.site.register(Recipient)
admin.site.register(Setting)
admin.site.register(Site)

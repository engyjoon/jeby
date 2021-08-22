from django.contrib import admin
from .models import Keyword, Setting, Site


admin.site.register(Keyword)
admin.site.register(Setting)
admin.site.register(Site)

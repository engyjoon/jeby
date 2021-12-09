from django.contrib import admin
from .models import Keyword, Recipient, Setting, Site


@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ["title", "content", "mailing", "author"]
    list_filter = ("author",)


admin.site.register(Recipient)
admin.site.register(Setting)
admin.site.register(Site)

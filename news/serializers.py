from rest_framework import serializers
from .models import Site, Setting


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['address', 'description']

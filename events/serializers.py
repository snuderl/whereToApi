from rest_framework import serializers
from .models import Place, Event


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


from rest_framework import serializers


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event


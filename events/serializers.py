from rest_framework import serializers
from .models import Place, Event
from rest_framework_gis.fields import GeometryField


class SimplePointField(GeometryField):
    def to_representation(self, value):
        if isinstance(value, dict) or value is None:
            return value
        # we expect value to be a GEOSGeometry instance
        return value.coords


class PlaceSerializer(serializers.ModelSerializer):
    coords = SimplePointField()

    class Meta:
        model = Place
        exclude = ("id", )


class EventSerializer(serializers.ModelSerializer):
    coords = SimplePointField()
    place_facebook_id = serializers.CharField(source="place.facebook_id")

    class Meta:
        model = Event
        exclude = ("id", "place")


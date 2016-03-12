from .models import Place, Event
from rest_framework import viewsets
from rest_framework_gis.filters import DistanceToPointFilter
from .serializers import EventSerializer, PlaceSerializer
from rest_framework import filters
import geocoder
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance


DEFAULT_DISTANCE = 4000


def location_name_filter(qs, query_params):
    if 'location_name' in query_params:
        g = geocoder.google(query_params['location_name'])
        point = Point(*g.latlng)

        distance = query_params.get('distance', str(DEFAULT_DISTANCE))
        print(point)
        return qs.filter(coords__distance_lt=(point, Distance(m=distance)))
    return qs


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    filter_backends = (DistanceToPointFilter, )
    bbox_filter_include_overlapping = True
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Place.objects.all()
        queryset = location_name_filter(queryset, self.request.query_params)
        return queryset


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    filter_backends = (DistanceToPointFilter, )
    bbox_filter_include_overlapping = True
    filter_backends = (filters.DjangoFilterBackend,)

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Event.objects.all()
        queryset = location_name_filter(queryset, self.request.query_params)
        return queryset


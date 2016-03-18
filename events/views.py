from .models import Place, Event
from rest_framework import viewsets
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework.response import Response
from .serializers import EventSerializer, PlaceSerializer
from rest_framework import filters
import geocoder
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from datetime import datetime
from .fb import fetch_places_query, add_place_by_id
from rest_framework.decorators import api_view



DEFAULT_DISTANCE = 4000


def location_name_filter(qs, query_params):
    if 'location_name' in query_params:
        g = geocoder.google(query_params['location_name'])
        point = Point(*g.latlng)

        distance = query_params.get('distance', str(DEFAULT_DISTANCE))
        return qs.filter(coords__distance_lt=(point, Distance(m=distance)))
    return qs


def keep_old_events(qs, query_params):
    keep_old = query_params.get('keep_old')
    if not keep_old:
        qs = qs.filter(start_time__gte=datetime.now())
    return qs


@api_view(['GET'])
def query_places(request):
    q = request.GET.get("q")

    data = fetch_places_query(q)
    serializer = PlaceSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_place(request, fb_id):
    place, created = add_place_by_id(fb_id)
    if created:
        return Response("Place added.")
    else:
        return Response("Place already exists.")


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
        queryset = keep_old_events(queryset, self.request.query_params)
        return queryset

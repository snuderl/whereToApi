from .models import Place, Event
from rest_framework import viewsets
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework.response import Response
from .serializers import EventSerializer, PlaceSerializer, EventPlaceSerializer
from rest_framework import filters
import geocoder
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from datetime import datetime
from .fb import fetch_places_query, add_place_by_id, FbError
from rest_framework.decorators import api_view
import django_filters
from django import forms


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


class LocationNameFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, qs, view):
        return location_name_filter(qs, request.query_params)


class KeepOldEventsFilter(filters.BaseFilterBackend):
    def filter_queryset(self, request, qs, view):
        return keep_old_events(qs, request.query_params)


@api_view(['GET'])
def query_places(request):
    q = request.GET.get("q")

    token = request.GET.get('token')
    if not token:
        return Response({"token": "Facebook token missing."}, status=400)

    try:
        data = fetch_places_query(q, token)
        data_ids = [x['facebook_id'] for x in data]
        existing_places = set(Place.objects.values_list("facebook_id", flat=True)
                                           .filter(facebook_id__in=data_ids))
        data = [x for x in data if x['facebook_id'] not in existing_places]
    except FbError as e:
        return Response(e.message(), status=400)

    serializer = PlaceSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_place(request, fb_id):
    token = request.GET.get('token')
    if not token:
        return Response({"token": "Facebook token missing."}, status=400)

    try:
        place, created = add_place_by_id(fb_id, token, add_events=True)
    except FbError as e:
        return Response(e.message(), status=400)
    if created:
        return Response("Place added.")
    else:
        return Response("Place already exists.")


def filter_keep_old(queryset, value):
    if value and value == "True":
        return queryset
    return queryset.filter(start_time__gte=datetime.now())


def filter_coords(queryset, value):
    distance = DEFAULT_DISTANCE
    print(value)
    if value:
        point = Point(*map(float, value.split(",")))
        return queryset.filter(coords__distance_lt=(point, Distance(m=distance)))
    return queryset


class EventsFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_type='icontains')
    keep_old = django_filters.ChoiceFilter(choices=(('True', 'True'), ('False', 'False')),
                                           action=filter_keep_old)
    coords = django_filters.CharFilter(action=filter_coords)

    class Meta:
        model = Event
        fields = ['name', 'place', 'coords']


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    filter_backends = (DistanceToPointFilter, LocationNameFilter)
    bbox_filter_include_overlapping = True
    lookup_field = 'facebook_id'


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('place')
    serializer_class = EventSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    bbox_filter_include_overlapping = True
    filter_backends = (filters.DjangoFilterBackend, )
    lookup_field = 'facebook_id'
    filter_class = EventsFilter


class EventPlaceViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().select_related('place')
    serializer_class = EventSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    filter_backends = (DistanceToPointFilter, LocationNameFilter, KeepOldEventsFilter)
    bbox_filter_include_overlapping = True
    lookup_field = 'facebook_id'

    def list(self, request):
        events = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(events)
        if page is not None:
            places = Place.objects.filter(id__in=set(x.place.id for x in page))
            serializer = EventPlaceSerializer({
                "events": page,
                "places": places
            })
            return self.get_paginated_response(serializer.data)

        places = Place.objects.filter(id__in=set(x.place.id for x in events))
        serializer = EventPlaceSerializer({
            "events": events,
            "places": places
        })
        return Response(serializer.data)

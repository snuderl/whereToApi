from django.shortcuts import render
from .models import Place, Event
from rest_framework import viewsets
from rest_framework_gis.filters import DistanceToPointFilter
from rest_framework.generics import ListAPIView
from .serializers import EventSerializer, PlaceSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    filter_backends = (DistanceToPointFilter, )
    bbox_filter_include_overlapping = True


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    distance_filter_field = 'coords'
    distance_filter_convert_meters = True
    filter_backends = (DistanceToPointFilter, )
    bbox_filter_include_overlapping = True


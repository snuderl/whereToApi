import requests
from .models import Place, Event
from django.contrib.gis.geos import Point
import aiohttp
import asyncio


base_url = "https://graph.facebook.com/v2.5/"
token = "CAACEdEose0cBANJd2muR06Aq3YbYmtX3nB53IqI4ZBzSlsE8joWHUXtLUKWYGYFWoxmPFakd3KTvResoQ3klHi2mZAyHZAt6VJJvreLIOOwMkZBWzOS0MZB2yCEzNK3VmedWFqoxBEtB8lqWw6SLAeIflbZAtgTYU4BYF5VOe75USambxrzQOUQwbeIH0WoZA71XVx2tnlxXZA9c0HDpudxF"


def parse_places(data):
  for place in data:
    loc = place["location"]
    point = Point(loc["latitude"], loc["longitude"], srid=4326)
    fb_id = place["id"]
    yield parse_place(place)


def parse_place(data):
  loc = data["location"]
  point = Point(loc["latitude"], loc["longitude"], srid=4326)
  fb_id = data["id"]
  return {
    "facebook_id": fb_id,
    "name": data["name"],
    "coords": point,
    "city": loc.get("city"),
    "country": loc.get("country"),
    "street": loc.get("street")
  }


def fetch_places(url, params={}):
  response = requests.get(url, params=params)
  print(response)

  data = response.json()
  for place in parse_places(data["data"]):
    yield place

  pagination = data["paging"]
  if pagination and "next" in pagination:
    next_url = pagination["next"]
    print(pagination)
    if next_url:
      print("Processing next page %s" % next_url)
      for place in fetch_places(next_url):
        yield place


def fetch_places_query(query):
  url = base_url + "/search"
  params = {
    "type": "place",
    "access_token": token,
    "limit": 500
  }

  if query:
    params["q"] = query

  return list(fetch_places(url, params))


def fetch_places_for_location(lat, lng):
  url = base_url + "/search"
  params = {
    "type": "place",
    "center": "%s,%s" % (lat, lng),
    "access_token": token
  }
  for place in fetch_places(url, params):
    Place.objets.update_or_create(**place)


def parse_events(data, place):
  for record in data:
    try:
      event = Event.objects.get(facebook_id=record["id"])
    except Event.DoesNotExist:
      event = Event(facebook_id=record["id"])

    try:
      event.name = record["name"]
      event.description = record.get("description")
      event.place = place
      event.attending_count = record.get("attending_count", 0)

      cover = record.get("cover")
      if cover:
        event.cover = cover["source"]

      owner = record.get('owner')
      if owner:
        event.owner = owner['name']

      event.start_time = record["start_time"]
      event.end_time = record.get('end_time')
      event.coords = place.coords

      event.save()
    except KeyError as e:
      print(e)


@asyncio.coroutine
def fetch_events(url, params={}, place=None):
  response = yield from aiohttp.get(url, params=params)
  print(response)

  data = (yield from response.json()).get("events")
  if not data:
    print("No events for %s" % place.name)
    return

  yield from parse_events(data["data"], place)

  pagination = data["paging"]
  if pagination and "next" in pagination:
    next_url = pagination["next"]
    print("Processing next page %s" % next_url)
    yield from fetch_events(next_url, place=place)


def fetch_events_by_location_name(name):
  g = geocoder.google(name)
  lat, lng = g.latlng


@asyncio.coroutine
def fetch_events_for_place(place):
  print("Fetching events for %s" % place.name)
  url = base_url + "/" + place.facebook_id
  params = {
    "fields": "events{attending_count,name,description,cover,start_time,end_time,owner}",
    "access_token": token
  }
  yield from fetch_events(url, params, place)
  print("Fetching events for %s complete." % place.name)


def fetch_all_events():
  loop = asyncio.get_event_loop()
  requests = [fetch_events_for_place(place) for place in Place.objects.all()]
  loop.run_until_complete(asyncio.wait(requests))
  print("Done")

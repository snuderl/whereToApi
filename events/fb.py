import requests
from .models import Place, Event
from django.contrib.gis.geos import Point

base_url = "https://graph.facebook.com/v2.5/"
token = "EAACEdEose0cBAFU7rm8GoVluZB3bp4dg4ocwOSecuZBVjYesYWGAg8yqZCbbv6JZABNNycoA1WUCprQf8bn7Shwa0vmKl1ov4fWLTOgjaPB0R3tHs5hFHZBqIbOg2MAnzqgXBXbzXZALP38TddHheCW4RLrf413Is225o75LCYZAgZDZD"


PLACE_FIELDS = {"fields": "location,name,id,picture.type(large),cover"}


class FbError(Exception):
  def __init__(self, response):
    super(FbError, self).__init__()
    self.response = response

  def message(self):
    data = self.response.json()
    error = data['error']
    return error


def parse_places(data):
  for place in data:
    yield parse_place(place)


def parse_place(data):
  loc = data["location"]
  point = Point(loc["latitude"], loc["longitude"], srid=4326)
  fb_id = data["id"]
  picture = None
  if 'picture' in data:
    picture = data['picture']['data']['url']
  cover = data.get("cover")
  if cover:
    cover = cover["source"]
  return {
    "facebook_id": fb_id,
    "name": data["name"],
    "coords": point,
    "city": loc.get("city"),
    "country": loc.get("country"),
    "street": loc.get("street"),
    "picture": picture,
    "cover": cover
  }


def fetch_places(url, params={}):
  response = requests.get(url, params=params)
  data = response.json()

  if response.status_code == requests.codes.ok:
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
  else:
    # if data["error"]["is_transient"]:
    #   print("Transient error for %s" % url)
    #   return
    print(data)
    raise FbError(response)


def fetch_places_query(query, token):
  url = base_url + "/search"
  params = {
    "type": "place",
    "access_token": token,
    "limit": 500
  }

  if query:
    params["q"] = query

  return list(fetch_places(url, params))


def add_place_by_id(fb_id, token, add_events=False):
  data = fetch_resource_by_id(fb_id, PLACE_FIELDS, token)
  place = parse_place(data)
  place, created = Place.objects.update_or_create(place, facebook_id=fb_id)

  if created and add_events:
    fetch_events_for_place(place, token)

  return place, created


def fetch_resource_by_id(fb_id, fields, token):
  url = base_url + "/" + fb_id
  params = {"access_token": token}
  params.update(fields)

  response = requests.get(url, params=params)
  return response.json()


def fetch_places_for_location(lat, lng, token, add_events=True):
  url = base_url + "/search"
  params = {
      "type": "place",
      "center": "%s,%s" % (lat, lng),
      "access_token": token
  }
  for place in fetch_places(url, params):
    place, created = add_place_by_id(place["facebook_id"], token, add_events)
    print (place, created)


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


def fetch_events(url, params={}, place=None, paginated=False):
  print(url, params)
  response = requests.get(url, params=params)
  json = response.json()

  if paginated:
    data = json
  else:
    data = json.get("events")
    if not data:
      return

  print(len(data["data"]), " events found for ", place.name)

  parse_events(data["data"], place)

  pagination = data["paging"]
  if pagination and "next" in pagination:
    next_url = pagination["next"]
    print("Processing next page %s" % next_url)
    fetch_events(next_url, place=place, paginated=True)


def fetch_events_by_location_name(name):
  g = geocoder.google(name)
  lat, lng = g.latlng


def fetch_events_for_place(place, token):
  print("Fetching events for %s" % place.name)
  url = base_url + "/" + place.facebook_id
  params = {
    "fields": "events{attending_count,name,description,cover,start_time,end_time,owner}",
    "access_token": token
  }
  fetch_events(url, params, place)
  print("Fetching events for %s complete." % place.name)


def fetch_all_events(token):
  for place in Place.objects.all().order_by('-id'):
    fetch_events_for_place(place, token)
  print("Done")

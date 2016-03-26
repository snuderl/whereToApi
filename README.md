# whereToApi

## Api calls

### Search for places on facebook [GET]
/fb/places?q={query}&token={fbToken}

query - search string
token - facebook api token

### Add place by id [POST]
/places/add/{fb_id}?token={fbToken}

token - facebook api token

### List places [GET]
/places?dist={distance}&point={point}

dist - distance in meters

point - latitude and longitude in format (lat, lng)

### List events [GET]
/events?dist={disance}&point={point}

dist - distance in meters

point - latitude and longitude in format (lat, lng)

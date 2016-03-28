from django.contrib.gis.db import models


class Place(models.Model):
  # Regular Django fields corresponding to the attributes in the
  # world borders shapefile.
  facebook_id = models.TextField(blank=True, null=True, unique=True)
  name = models.CharField(max_length=200)
  coords = models.PointField()
  city = models.TextField(blank=True, null=True)
  country = models.TextField(blank=True, null=True)
  street = models.TextField(blank=True, null=True)
  picture = models.TextField(blank=True, null=True)
  objects = models.GeoManager()

  def __str__(self):
      return self.name


class Event(models.Model):
  name = models.TextField()
  description = models.TextField(blank=True, null=True)
  place = models.ForeignKey(Place)
  attending_count = models.IntegerField()
  facebook_id = models.TextField(blank=True, null=True, unique=True)

  owner = models.TextField()
  cover = models.TextField()
  start_time = models.DateTimeField()
  end_tiem = models.DateTimeField(blank=True, null=True)

  coords = models.PointField()


  last_updated = models.DateTimeField(auto_now=True)

from django.contrib.gis.db import models


class Place(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    facebook_id = models.IntegerField(blank=True, null=True, unique=True)
    name = models.CharField(max_length=50)
    coords = models.PointField()
    objects = models.GeoManager()

    def __str__(self):
        return self.name


class Event(models.Model):
	name = models.TextField()
	place = models.ForeignKey(Place)
	facebook_id = models.IntegerField(blank=True, null=True, unique=True)
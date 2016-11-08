from django.contrib import admin
from events.models import Place, Event


class PlaceAdmin(admin.ModelAdmin):
  list_display = ('name', 'city')
  search_fields = ('name', )


class EventAdmin(admin.ModelAdmin):
  list_display = ('name', 'place_name', 'start_time', 'end_time')
  search_fields = ('name', 'place__name')

  def place_name(self, obj):
    return obj.place.name


admin.site.register(Place, PlaceAdmin)
admin.site.register(Event, EventAdmin)

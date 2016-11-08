from django.contrib import admin
from events.models import Place, Event


class PlaceAdmin(admin.ModelAdmin):
    pass


class EventAdmin(admin.ModelAdmin):
    pass


admin.site.register(Place, PlaceAdmin)
admin.site.register(Event, EventAdmin)

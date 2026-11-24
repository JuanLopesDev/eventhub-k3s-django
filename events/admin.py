from django.contrib import admin
from .models import ContactRecord, Event

admin.site.register(Event)
admin.site.register(ContactRecord)


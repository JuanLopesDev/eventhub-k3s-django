from datetime import date, time
from django.test import TestCase
from django.urls import reverse
from .models import ContactRecord, Event


class EventViewsTests(TestCase):
    def setUp(self):
        self.event = Event.objects.create(name="Seminário", description="Teste", date=date(2026, 12, 1), time=time(9, 0), location="Sala 1", responsible="Ana")

    def test_event_search_returns_match(self):
        response = self.client.get(reverse("events:list"), {"q": "Semin"})
        self.assertContains(response, "Seminário")

    def test_contact_form_persists_record(self):
        response = self.client.post(reverse("events:contact_create"), {"name": "João", "email": "joao@example.com", "message": "Olá"})
        self.assertRedirects(response, reverse("events:contacts"))
        self.assertTrue(ContactRecord.objects.filter(email="joao@example.com").exists())

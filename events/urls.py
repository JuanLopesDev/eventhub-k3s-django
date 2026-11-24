from django.urls import path
from . import views

app_name = "events"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("health/", views.health, name="health"),
    path("eventos/", views.EventListView.as_view(), name="list"),
    path("eventos/novo/", views.EventCreateView.as_view(), name="create"),
    path("eventos/<int:pk>/", views.EventDetailView.as_view(), name="detail"),
    path("eventos/<int:pk>/editar/", views.EventUpdateView.as_view(), name="update"),
    path("eventos/<int:pk>/excluir/", views.EventDeleteView.as_view(), name="delete"),
    path("contatos/", views.ContactListView.as_view(), name="contacts"),
    path("contatos/novo/", views.contact_create, name="contact_create"),
]


import os
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from .forms import ContactRecordForm, EventForm
from .models import ContactRecord, Event


def dashboard(request):
    return render(request, "events/dashboard.html", {"upcoming": Event.objects.exclude(status=Event.Status.CANCELLED)[:5], "total": Event.objects.count(), "pod_name": os.getenv("HOSTNAME", "desenvolvimento")})


def health(request):
    return HttpResponse("ok", content_type="text/plain")


class EventListView(ListView):
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        qs = super().get_queryset()
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(location__icontains=query) | Q(responsible__icontains=query))
        return qs


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    success_url = reverse_lazy("events:list")

    def form_valid(self, form):
        messages.success(self.request, "Evento cadastrado com sucesso.")
        return super().form_valid(form)


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"


class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"

    def get_success_url(self):
        messages.success(self.request, "Evento atualizado com sucesso.")
        return reverse_lazy("events:detail", kwargs={"pk": self.object.pk})


class EventDeleteView(DeleteView):
    model = Event
    template_name = "events/event_confirm_delete.html"
    success_url = reverse_lazy("events:list")

    def form_valid(self, form):
        messages.success(self.request, "Evento excluído com sucesso.")
        return super().form_valid(form)


def contact_create(request):
    form = ContactRecordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Registro enviado com sucesso.")
        return redirect("events:contacts")
    return render(request, "events/contact_form.html", {"form": form})


class ContactListView(ListView):
    model = ContactRecord
    template_name = "events/contact_list.html"
    context_object_name = "contacts"


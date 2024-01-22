from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.query import QuerySet
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from notes.models import Note

# Generic views use a template at <app>/<model>_<viewtype>.html
# Create and update views share a template at <app>/<model>_form.html


class BelongsToUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        if obj and obj.user:
            return self.request.user == obj.user
        return False


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    context_object_name = "notes"

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user).order_by("-created")


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    context_object_name = "note"
    fields = ("title", "content")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteDetailView(BelongsToUserMixin, DetailView):
    model = Note
    context_object_name = "note"
    fields = ("title", "content")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteUpdateView(BelongsToUserMixin, UpdateView):
    model = Note
    context_object_name = "note"
    fields = ("title", "content")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteDeleteView(BelongsToUserMixin, DeleteView):
    model = Note
    context_object_name = "note"
    success_url = "/notes/"

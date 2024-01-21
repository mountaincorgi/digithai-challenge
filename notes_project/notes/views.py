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
class NoteListView(ListView):
    model = Note
    context_object_name = "notes"
    ordering = ["-created"]


class NoteCreateView(CreateView):
    model = Note
    context_object_name = "note"
    fields = ("title", "content")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteDetailView(DetailView):
    model = Note
    context_object_name = "note"
    fields = ("title", "content")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteUpdateView(UpdateView):
    model = Note
    context_object_name = "note"
    fields = ("title", "content")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class NoteDeleteView(DeleteView):
    model = Note
    context_object_name = "note"
    success_url = "/notes"

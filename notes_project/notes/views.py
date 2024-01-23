from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.query import Q
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from notes.forms import SearchForm
from notes.models import Note

# Generic views use a template at <app>/<model>_<viewtype>.html
# Create and update views share a template at <app>/<model>_form.html


class BelongsToUserMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Users must be authenticated and own the requested view object."""

    def test_func(self):
        obj = self.get_object()
        if obj and obj.user:
            return self.request.user == obj.user
        return False


class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    context_object_name = "notes"

    def get(self, request, *args, **kwargs):
        form = SearchForm(request.GET)
        search_query = request.GET.get("q", "")

        filter_q_obj = self.get_search_q_object(search_query) & Q(
            user=self.request.user
        )
        self.object_list = Note.objects.filter(filter_q_obj).order_by(
            "-created"
        )
        context = {"form": form, "notes": self.object_list}
        return self.render_to_response(context)

    def get_search_q_object(self, search_query: str) -> Q:
        """Build a Q object to filter Notes by their titles.

        Each group of characters separated by spaces is treated as a separate
        search item. i.e. if there are 2 notes, 'Note One' and 'Note Two,
        searching by 'one two' will return both notes.
        """

        q_obj = Q()

        if search_query:
            search_items = search_query.split()
            for item in search_items:
                q_obj |= Q(title__icontains=item)

        return q_obj


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
    success_url = "/"

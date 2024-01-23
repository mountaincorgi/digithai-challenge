from django.test import TestCase
from notes.factories import NoteFactory


class NoteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.note = NoteFactory()

    def test_string_representation_is_the_same_as_the_title(self):
        assert str(self.note) == self.note.title

    def test_first_name_label(self):
        field_label = self.note._meta.get_field("title").verbose_name
        assert field_label == "Title"

    def test_content_label(self):
        field_label = self.note._meta.get_field("content").verbose_name
        assert field_label == "Content"

    def test_created_label(self):
        field_label = self.note._meta.get_field("created").verbose_name
        assert field_label == "Created"

    def test_modified_label(self):
        field_label = self.note._meta.get_field("modified").verbose_name
        assert field_label == "Modified"

    def test_title_max_length(self):
        max_length = self.note._meta.get_field("title").max_length
        assert max_length == 140

    def test_content_preview_cuts_off_at_180_characters(self):
        note = NoteFactory(
            content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum maximus dictum massa, sit amet vehicula purus laoreet nec. Nam iaculis dignissim eros, et elementum ex imperdiet id."
        )
        assert (
            note.preview_content
            == "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum maximus dictum massa, sit amet vehicula purus laoreet nec. Nam iaculis dignissim eros, et elementum ex imperd..."
        )

    def test_content_preview_under_180_characters_stays_the_same(self):
        note = NoteFactory(content="Less than 180 characters!")
        assert note.content == "Less than 180 characters!"

    def test_get_absolute_url(self):
        assert self.note.get_absolute_url() == f"/{self.note.pk}/"

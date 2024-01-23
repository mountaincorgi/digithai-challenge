from datetime import datetime

from django.test import Client, TestCase
from notes.factories import NoteFactory
from notes.models import Note
from notes.views import NoteListView
from pytz import UTC
from users.factories import UserFactory


class NoteListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)

    def setUp(self):
        self.client.force_login(self.user_1)

    def test_get_request_renders_the_note_list_template(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "notes/note_list.html")

    def test_notes_are_ordered_from_newest_to_oldest(self):
        note_1 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 2, tzinfo=UTC)
        )
        note_2 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 1, tzinfo=UTC)
        )
        note_3 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 3, tzinfo=UTC)
        )
        response = self.client.get("/")
        notes = response.context["notes"]
        assert list(notes) == [note_3, note_1, note_2]

    def test_user_cannot_see_notes_belonging_to_other_users(self):
        note_1 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 1, tzinfo=UTC)
        )
        note_2 = NoteFactory(
            user=self.user_2, custom_created=datetime(2024, 1, 1, tzinfo=UTC)
        )
        response = self.client.get("/")
        notes = response.context["notes"]
        assert list(notes) == [note_1]

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = Client().get("/")
        self.assertRedirects(response, "/login/?next=/")

    def test_searching_notes_using_a_querystring_is_possible(self):
        note_1 = NoteFactory(user=self.user_1, title="one")
        note_2 = NoteFactory(user=self.user_1, title="two")

        response = self.client.get("/?q=one")
        notes = response.context["notes"]
        assert list(notes) == [note_1]

    def test_searching_with_an_invalid_querystring_returns_all_notes(self):
        note_1 = NoteFactory(user=self.user_1, title="one")
        note_2 = NoteFactory(user=self.user_1, title="two")

        response = self.client.get("/?qqq=one")
        notes = response.context["notes"]
        self.assertCountEqual(notes, [note_1, note_2])


class GetSearchQObjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.view = NoteListView()

        cls.note_1 = NoteFactory(title="Diary Entry", content="content")
        cls.note_2 = NoteFactory(title="shopping list!!", content="content")
        cls.note_3 = NoteFactory(title="New Year 2023", content="content")
        cls.note_4 = NoteFactory(title="my BUCKET LIST", content="content")

    def test_searching_with_exact_word_works(self):
        q_obj = self.view.get_search_q_object("Diary")
        notes = Note.objects.filter(q_obj)
        assert list(notes) == [self.note_1]

    def test_searching_with_a_substring_works(self):
        q_obj = self.view.get_search_q_object("shop")
        notes = Note.objects.filter(q_obj)
        assert list(notes) == [self.note_2]

    def test_searching_is_not_case_sensitive(self):
        q_obj = self.view.get_search_q_object("DIARY")
        notes = Note.objects.filter(q_obj)
        assert list(notes) == [self.note_1]

    def test_searching_with_numbers_works(self):
        q_obj = self.view.get_search_q_object("2023")
        notes = Note.objects.filter(q_obj)
        assert list(notes) == [self.note_3]

    def test_searching_with_special_characters_works(self):
        q_obj = self.view.get_search_q_object("!!")
        notes = Note.objects.filter(q_obj)
        assert list(notes) == [self.note_2]

    def test_searching_can_match_more_than_one_item(self):
        q_obj = self.view.get_search_q_object("list")
        notes = Note.objects.filter(q_obj)
        self.assertCountEqual(notes, [self.note_2, self.note_4])

    def test_whitespace_is_stripped_from_the_search_query(self):
        q_obj = self.view.get_search_q_object("diary         shop   ")
        notes = Note.objects.filter(q_obj)
        self.assertCountEqual(notes, [self.note_1, self.note_2])

    def test_words_separated_by_spaces_become_separate_search_items(self):
        q_obj = self.view.get_search_q_object("diary shop")
        notes = Note.objects.filter(q_obj)
        self.assertCountEqual(notes, [self.note_1, self.note_2])

    def test_searching_with_a_blank_string_returns_all_notes(self):
        q_obj = self.view.get_search_q_object("")
        notes = Note.objects.filter(q_obj)
        self.assertCountEqual(
            notes, [self.note_1, self.note_2, self.note_3, self.note_4]
        )

    def test_return_no_results_if_no_titles_match_the_search_query(self):
        q_obj = self.view.get_search_q_object("random")
        notes = Note.objects.filter(q_obj)
        assert not notes.exists()

    def test_searching_by_pk_does_not_work(self):
        q_obj = self.view.get_search_q_object(f"{self.note_1.pk}")
        notes = Note.objects.filter(q_obj)
        assert not notes.exists()

    def test_searching_by_content_does_not_work(self):
        q_obj = self.view.get_search_q_object("content")
        notes = Note.objects.filter(q_obj)
        assert not notes.exists()


class NoteCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)

    def setUp(self):
        self.client.force_login(self.user_1)

    def test_get_request_renders_the_note_form_template(self):
        response = self.client.get("/create/")
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_redirect_to_the_note_detail_page_after_creating_a_note(self):
        response = self.client.post("/create/", {"title": "a", "content": "b"})
        note = Note.objects.first()
        self.assertRedirects(response, f"/{note.pk}/")

    def test_submitting_invalid_form_data_reloads_the_page(self):
        response = self.client.post("/create/", {"title": "", "content": "b"})
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_submitting_invalid_form_data_does_not_create_a_note(self):
        self.client.post("/create/", {"title": "", "content": "b"})
        assert not Note.objects.exists()

    def test_user_cannot_make_notes_for_other_users(self):
        self.client.post(
            "/create/", {"title": "a", "content": "b", "user": self.user_2.pk}
        )
        note = Note.objects.first()
        assert note.user == self.user_1

    def test_unauthenticated_user_get_is_redirected_to_the_login_page(self):
        response = Client().get("/create/")
        self.assertRedirects(response, "/login/?next=/create/")

    def test_unauthenticated_user_post_is_redirected_to_the_login_page(self):
        response = Client().post("/create/", {"title": "a", "content": "b"})
        self.assertRedirects(response, "/login/?next=/create/")


class NoteDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def setUp(self):
        self.client.force_login(self.user_1)

    def test_get_request_renders_the_note_detail_template(self):
        response = self.client.get(f"/{self.note_1.pk}/")
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_user_cannot_read_a_note_belonging_to_another_user(self):
        response = self.client.get(f"/{self.note_2.pk}/")
        assert response.status_code == 403

    def test_user_cannot_read_a_note_that_does_not_exist(self):
        response = self.client.get("/1000000/")
        assert response.status_code == 404

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = Client().get(f"/{self.note_1.pk}/")
        self.assertRedirects(response, f"/login/?next=/{self.note_1.pk}/")


class NoteUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def setUp(self):
        self.client.force_login(self.user_1)

    def test_get_request_renders_the_note_form_template(self):
        response = self.client.get(f"/{self.note_1.pk}/update/")
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_user_can_update_their_own_note(self):
        self.client.post(
            f"/{self.note_1.pk}/update/", {"title": "a", "content": "b"}
        )
        note = Note.objects.get(user=self.user_1)
        assert note.title == "a" and note.content == "b"

    def test_redirect_to_the_note_detail_page_after_updating_a_note(self):
        response = self.client.post(
            f"/{self.note_1.pk}/update/", {"title": "a", "content": "b"}
        )
        self.assertRedirects(response, f"/{self.note_1.pk}/")

    def test_user_cannot_update_a_note_belonging_to_another_user(self):  # 403
        response = self.client.post(
            f"/{self.note_2.pk}/update/",
            {"title": "a", "content": "b"},
        )
        assert response.status_code == 403

    def test_user_cannot_update_a_note_that_does_not_exist(self):
        response = self.client.post(
            "/1000000/update/",
            {"title": "a", "content": "b"},
        )
        assert response.status_code == 404

    def test_user_cannot_update_a_note_with_an_invalid_pk(self):
        response = self.client.post(
            "/one/update/",
            {"title": "a", "content": "b"},
        )
        assert response.status_code == 404

    def test_submitting_invalid_form_data_reloads_the_page(self):
        response = self.client.post(
            f"/{self.note_1.pk}/update/", {"title": "", "content": "b"}
        )
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_submitting_invalid_form_does_not_update_a_note(self):
        self.client.post(
            f"/{self.note_1.pk}/update/",
            {"title": "", "content": "b"},
        )
        note = Note.objects.get(user=self.user_1)
        assert not note.title == "" and not note.content == "b"

    def test_unauthenticated_user_get_is_redirected_to_the_login_page(self):
        response = Client().get(f"/{self.note_1.pk}/update/")
        self.assertRedirects(
            response, f"/login/?next=/{self.note_1.pk}/update/"
        )

    def test_unauthenticated_user_post_is_redirected_to_the_login_page(self):
        response = Client().post(
            f"/{self.note_1.pk}/update/", {"title": "a", "content": "b"}
        )
        self.assertRedirects(
            response, f"/login/?next=/{self.note_1.pk}/update/"
        )


class NoteDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def setUp(self):
        self.client.force_login(self.user_1)

    def test_get_request_renders_the_note_confirm_delete_template(self):
        response = self.client.get(f"/{self.note_1.pk}/delete/")
        self.assertTemplateUsed(response, "notes/note_confirm_delete.html")

    def test_user_can_delete_their_own_note(self):
        self.client.post(f"/{self.note_1.pk}/delete/")
        assert not Note.objects.filter(user=self.user_1).exists()

    def test_redirect_to_notes_list_after_deleting_a_note(self):
        response = self.client.post(f"/{self.note_1.pk}/delete/")
        self.assertRedirects(response, "/")

    def test_user_cannot_delete_a_note_belonging_to_another_user(self):
        response = self.client.post(f"/{self.note_2.pk}/delete/")
        assert response.status_code == 403

    def test_user_cannot_delete_a_note_that_does_not_exist(self):
        response = self.client.post("/1000000/delete/")
        assert response.status_code == 404

    def test_user_cannot_delete_a_note_that_with_an_invalid_pk(self):
        response = self.client.post("/one/delete/")
        assert response.status_code == 404

    def test_unauthenticated_user_get_is_redirected_to_the_login_page(self):
        response = Client().get(f"/{self.note_1.pk}/delete/")
        self.assertRedirects(
            response, f"/login/?next=/{self.note_1.pk}/delete/"
        )

    def test_unauthenticated_user_post_is_redirected_to_the_login_page(self):
        response = Client().post(f"/{self.note_1.pk}/delete/")
        self.assertRedirects(
            response, f"/login/?next=/{self.note_1.pk}/delete/"
        )

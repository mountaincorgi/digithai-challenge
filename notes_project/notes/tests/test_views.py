from datetime import datetime

from django.test import RequestFactory, TestCase
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
        self.factory = RequestFactory()

    def test_get_request_renders_the_note_list_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get("/notes/")
        self.assertTemplateUsed(response, "notes/note_list.html")

    def test_notes_ordered_from_newest_to_oldest(self):
        note_1 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 2, tzinfo=UTC)
        )
        note_2 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 1, tzinfo=UTC)
        )
        note_3 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 3, tzinfo=UTC)
        )

        request = self.factory.get("/notes/")
        request.user = self.user_1
        response = NoteListView.as_view()(request)
        notes = response.context_data["notes"]
        self.assertListEqual(list(notes), [note_3, note_1, note_2])

    def test_user_cannot_see_other_users_notes(self):
        note_1 = NoteFactory(
            user=self.user_1, custom_created=datetime(2024, 1, 1, tzinfo=UTC)
        )
        note_2 = NoteFactory(
            user=self.user_2, custom_created=datetime(2024, 1, 1, tzinfo=UTC)
        )

        request = self.factory.get("/notes/")
        request.user = self.user_1
        response = NoteListView.as_view()(request)
        notes = response.context_data["notes"]
        self.assertListEqual(list(notes), [note_1])

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = self.client.get("/notes/")
        self.assertRedirects(response, "/login/?next=/notes/")

    def test_searching_works(self):
        self.client.force_login(self.user_1)
        note_1 = NoteFactory(
            user=self.user_1,
            title="one",
            custom_created=datetime(2024, 1, 1, tzinfo=UTC),
        )
        note_2 = NoteFactory(
            user=self.user_1,
            title="two",
            custom_created=datetime(2024, 1, 2, tzinfo=UTC),
        )

        response = self.client.get("/notes/?q=one")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [note_1])

    def test_searching_with_an_invalid_querystring_returns_all_notes(self):
        self.client.force_login(self.user_1)
        note_1 = NoteFactory(
            user=self.user_1,
            title="one",
            custom_created=datetime(2024, 1, 1, tzinfo=UTC),
        )
        note_2 = NoteFactory(
            user=self.user_1,
            title="two",
            custom_created=datetime(2024, 1, 2, tzinfo=UTC),
        )

        response = self.client.get("/notes/?qqq=one")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [note_2, note_1])


class GetSearchQObjectTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.view = NoteListView()

        cls.note_1 = NoteFactory(title="Diary Entry", content="content")
        cls.note_2 = NoteFactory(title="shopping list!!", content="content")
        cls.note_3 = NoteFactory(title="New Year 2023", content="content")
        cls.note_4 = NoteFactory(title="my BUCKET LIST", content="content")
        cls.note_5 = NoteFactory(title="restaurants list", content="content")

    def test_searching_by_exact_word_filters_notes_successfully(self):
        q_obj = self.view.get_search_q_object("Diary")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_1])

    def test_searching_by_a_substring_filters_notes_successfully(self):
        q_obj = self.view.get_search_q_object("shop")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_2])

    def test_searching_by_more_than_1_word_includes_results_with_either(self):
        q_obj = self.view.get_search_q_object("diary shop")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_1, self.note_2])

    def test_whitespace_is_stripped(self):
        q_obj = self.view.get_search_q_object("Diary         shop   ")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_1, self.note_2])

    def test_searching_is_not_case_sensitive(self):
        q_obj = self.view.get_search_q_object("DIAR")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_1])

    def test_searching_works_with_numbers(self):
        q_obj = self.view.get_search_q_object("2023")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_3])

    def test_searching_works_with_special_characters(self):
        q_obj = self.view.get_search_q_object("!!")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(list(notes), [self.note_2])

    def test_searching_with_a_blank_string_returns_all_notes(self):
        q_obj = self.view.get_search_q_object("")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertListEqual(
            list(notes),
            [self.note_1, self.note_2, self.note_3, self.note_4, self.note_5],
        )

    def test_searching_returns_no_matches(self):
        q_obj = self.view.get_search_q_object("random")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertFalse(notes.exists())

    def test_searching_by_pk_does_not_work(self):
        q_obj = self.view.get_search_q_object(f"{self.note_1.pk}")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertFalse(notes.exists())

    def test_searching_by_content_does_not_work(self):
        q_obj = self.view.get_search_q_object("content")
        notes = Note.objects.filter(q_obj).order_by("id")
        self.assertFalse(notes.exists())


class NoteCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)

    def test_get_request_renders_the_note_form_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get("/notes/create/")
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_successfully_creating_a_note_redirects_to_its_detail_page(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create/", {"title": "note", "content": "content"}
        )
        pk = Note.objects.first().pk
        self.assertRedirects(response, f"/notes/{pk}/")

    def test_submitting_invalid_form_data_reloads_the_page(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create/", {"title": "", "content": "content"}
        )
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_submitting_invalid_form_does_not_create_a_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create/", {"title": "", "content": "content"}
        )
        self.assertFalse(Note.objects.exists())

    def test_user_forced_to_be_the_request_user_when_creating_a_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create/",
            {"title": "note", "content": "content", "user": self.user_2.pk},
        )
        user = Note.objects.first().user
        self.assertEqual(user, self.user_1)

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = self.client.post(
            "/notes/create/", {"title": "note", "content": "content"}
        )
        self.assertRedirects(response, "/login/?next=/notes/create/")


class NoteDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def test_get_request_renders_the_note_detail_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/")
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_user_can_read_their_own_note(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/")  # status
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_user_cannot_see_a_note_created_by_another_user(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_2.pk}/")  # 403
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_read_a_note_that_does_not_exist(self):  # 404
        self.client.force_login(self.user_1)
        response = self.client.get("/notes/1000000/")
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = self.client.get(f"/notes/{self.note_1.pk}/")
        self.assertRedirects(
            response, f"/login/?next=/notes/{self.note_1.pk}/"
        )


class NoteUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def test_get_request_renders_the_note_form_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/update/")
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_redirect_to_the_note_detail_page_after_update(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update/",
            {"title": "note", "content": "content"},
        )
        self.assertRedirects(response, f"/notes/{self.note_1.pk}/")

    def test_user_can_update_their_own_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update/",
            {"title": "note", "content": "content"},
        )
        self.assertRedirects(response, f"/notes/{self.note_1.pk}/")

    def test_user_cannot_update_a_note_created_by_another_user(self):  # 403
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_2.pk}/update/",
            {"title": "note", "content": "content"},
        )
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_update_a_note_that_does_not_exist(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/1000000/update/",
            {"title": "note", "content": "content"},
        )
        self.assertEqual(response.status_code, 404)

    def test_submitting_invalid_form_data_reloads_the_page(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update/",
            {"title": "", "content": "content"},
        )
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_submitting_invalid_form_does_not_create_a_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update/",
            {"title": "", "content": "content"},
        )
        note = Note.objects.get(user=self.user_1)
        self.assertFalse(note.title == "")

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update/",
            {"title": "note", "content": "content"},
        )
        self.assertRedirects(
            response, f"/login/?next=/notes/{self.note_1.pk}/update/"
        )


class NoteDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def test_get_request_renders_the_note_confirm_delete_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/delete/")
        self.assertTemplateUsed(response, "notes/note_confirm_delete.html")

    def test_user_can_delete_their_own_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(f"/notes/{self.note_1.pk}/delete/")
        self.assertRedirects(response, "/notes/")

    def test_redirect_to_notes_list_after_deletion(self):
        self.client.force_login(self.user_1)
        response = self.client.post(f"/notes/{self.note_1.pk}/delete/")
        self.assertRedirects(response, "/notes/")

    def test_user_cannot_delete_a_note_created_by_another_user(self):
        self.client.force_login(self.user_1)
        response = self.client.post(f"/notes/{self.note_2.pk}/delete/")
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_delete_a_note_that_does_not_exist(self):
        self.client.force_login(self.user_1)
        response = self.client.post("/notes/1000000/delete/")
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        response = self.client.post(f"/notes/{self.note_1.pk}/delete/")
        self.assertRedirects(
            response, f"/login/?next=/notes/{self.note_1.pk}/delete/"
        )

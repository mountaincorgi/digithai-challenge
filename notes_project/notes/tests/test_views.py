from django.test import Client, TestCase
from notes.factories import NoteFactory
from users.factories import UserFactory


class NoteListTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)

    def test_get_request_renders_the_note_list_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get("/notes/")
        self.assertTemplateUsed(response, "notes/note_list.html")

    def test_notes_ordered_from_newest_to_oldest(self):
        self.client.force_login(self.user_1)

        note_1 = NoteFactory(
            user=self.user_1, custom_created="2022-01-01 00:00:00"
        )
        note_2 = NoteFactory(
            user=self.user_1, custom_created="2021-01-01 00:00:00"
        )
        note_3 = NoteFactory(
            user=self.user_1, custom_created="2023-01-01 00:00:00"
        )

        response = self.client.get("/notes/")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [note_3, note_1, note_2])

    def test_user_cannot_see_other_users_notes(self):
        self.client.force_login(self.user_1)

        note_1 = NoteFactory(
            user=self.user_1, custom_created="2024-01-01 00:00:00"
        )
        note_2 = NoteFactory(
            user=self.user_1, custom_created="2024-01-02 00:00:00"
        )
        note_3 = NoteFactory(
            user=self.user_2, custom_created="2024-01-03 00:00:00"
        )

        response = self.client.get("/notes/")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [note_2, note_1])

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        client = Client()
        response = client.get("/notes/")
        self.assertRedirects(response, "/login/")


class NoteListSearchTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

        cls.note_1 = NoteFactory(
            title="Diary Entry",
            content="content",
            custom_created="2024-01-01 00:00:00",
        )
        cls.note_2 = NoteFactory(
            title="shopping list!!",
            content="content",
            custom_created="2024-01-02 00:00:00",
        )
        cls.note_3 = NoteFactory(
            title="New Year 2023",
            content="content",
            custom_created="2024-01-03 00:00:00",
        )
        cls.note_4 = NoteFactory(
            title="my BUCKET LIST",
            content="content",
            custom_created="2024-01-04 00:00:00",
        )
        cls.note_5 = NoteFactory(
            title="restaurants list",
            content="content",
            custom_created="2000-01-05 00:00:00",
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_searching_by_exact_word_filters_notes_successfully(self):
        response = self.client.get("/notes/?search=Diary")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_1])

    def test_searching_by_a_substring_filters_notes_successfully(self):
        response = self.client.get("/notes/?search=shop")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_2])

    def test_searching_by_more_than_1_word_includes_results_with_either(self):
        pass

    def test_searching_is_not_case_sensitive(self):
        response = self.client.get("/notes/?search=DIAR")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_1])

    def test_searching_works_with_numbers(self):
        response = self.client.get("/notes/?search=2023")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_3])

    def test_searching_works_with_special_characters(self):
        response = self.client.get("/notes/?search=%2B")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_2])

    def test_searching_strips_whitespace_from_the_search_term(self):
        response = self.client.get("/notes/?search=%2B")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_2])

    def searching_returns_notes_ordered_from_newest_to_oldest(self):
        response = self.client.get("/notes/?search=list")
        notes = response.context["notes"]
        self.assertListEqual(
            list(notes), [self.note_4, self.note_2, self.note_5]
        )

    def test_searching_with_a_blank_string_returns_all_notes(self):
        response = self.client.get("/notes/?saarchh=")
        notes = response.context["notes"]
        self.assertListEqual(
            list(notes),
            [self.note_4, self.note_3, self.note_2, self.note_1, self.note_5],
        )

    def test_searching_with_an_invalid_querystring_returns_all_notes(self):
        response = self.client.get("/notes/?saarchh=random")
        notes = response.context["notes"]
        self.assertListEqual(
            list(notes),
            [self.note_4, self.note_3, self.note_2, self.note_1, self.note_5],
        )

    def test_manually_typed_spaces_are_removed_from_search_term(self):
        response = self.client.get("/notes/?search=dia   ry")
        notes = response.context["notes"]
        self.assertListEqual(list(notes), [self.note_1])

    def test_searching_returns_no_matches(self):
        response = self.client.get("/notes/?search=random")
        notes = response.context["notes"]
        self.assertFalse(notes.exists())

    def test_searching_by_pk_does_not_work(self):
        response = self.client.get(f"/notes/?search={self.note_1.pk}")
        notes = response.context["notes"]
        self.assertFalse(notes.exists())

    def test_searching_by_content_does_not_work(self):
        response = self.client.get("/notes/?search=content")
        notes = response.context["notes"]
        self.assertFalse(notes.exists())


class NoteCreateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)

    def test_get_request_renders_the_note_form_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get("/notes/create")
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_user_can_create_their_own_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create", {"title": "Note 1", "content": "content"}
        )
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_submitting_invalid_form_data_reloads_the_page(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create", {"title": "", "content": "content"}
        )
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_user_cannot_create_notes_for_other_users(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/create",
            {"title": "Note 1", "content": "content", "user": self.user_2.pk},
        )
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        client = Client()
        response = client.post(
            "/notes/create", {"title": "Note 1", "content": "content"}
        )
        self.assertRedirects(response, "/login/")


class NoteDetailTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def test_get_request_renders_the_note_detail_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/detail")
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_user_can_read_their_own_note(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/detail")
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_user_cannot_see_a_note_created_by_another_user(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_2.pk}/detail")
        self.assertRaises(response, 403)

    def test_user_cannot_read_a_note_that_does_not_exist(self):  # 404
        self.client.force_login(self.user_1)
        response = self.client.get("/notes/1000000/detail")
        self.assertRaises(response, 404)

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        client = Client()
        response = client.get(f"/notes/{self.note_1.pk}/detail")
        self.assertRedirects(response, "/login/")


class NoteUpdateTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def test_get_request_renders_the_note_form_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/update")
        self.assertTemplateUsed(response, "notes/note_form.html")

    def test_user_can_update_their_own_note(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update",
            {"title": "Note 1", "content": "content"},
        )
        self.assertTemplateUsed(response, "notes/note_detail.html")

    def test_user_cannot_update_a_note_created_by_another_user(self):  # 403
        self.client.force_login(self.user_1)
        response = self.client.post(
            f"/notes/{self.note_2.pk}/update",
            {"title": "Note 2", "content": "content"},
        )
        self.assertRaises(response, 403)

    def test_user_cannot_update_a_note_that_does_not_exist(self):
        self.client.force_login(self.user_1)
        response = self.client.post(
            "/notes/1000000/update",
            {"title": "Note 2", "content": "content"},
        )
        self.assertRaises(response, 404)

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        client = Client()
        response = client.post(
            f"/notes/{self.note_1.pk}/update",
            {"title": "Note 1", "content": "content"},
        )
        self.assertRedirects(response, "/login/")


class NoteDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1, cls.user_2 = UserFactory.create_batch(2)
        cls.note_1 = NoteFactory(user=cls.user_1)
        cls.note_2 = NoteFactory(user=cls.user_2)

    def test_get_request_renders_the_note_confirm_delete_template(self):
        self.client.force_login(self.user_1)
        response = self.client.get(f"/notes/{self.note_1.pk}/delete")
        self.assertTemplateUsed(response, "notes/note_confirm_delete.html")

    def test_user_can_delete_their_own_note(self):
        response = self.client.post(
            f"/notes/{self.note_1.pk}/update",
            {"title": "Note 1", "content": "content"},
        )
        self.assertRedirects(response, "/notes/")

    def test_user_cannot_delete_a_note_created_by_another_user(self):
        response = self.client.post(
            f"/notes/{self.note_2.pk}/update",
            {"title": "Note 1", "content": "content"},
        )
        self.assertRaises(response, 403)

    def test_user_cannot_delete_a_note_that_does_not_exist(self):
        response = self.client.post(
            "/notes/1000000/update",
            {"title": "Note 1", "content": "content"},
        )
        self.assertRaises(response, 404)

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        client = Client()
        response = client.post(
            f"/notes/{self.note_1.pk}/update",
            {"title": "Note 1", "content": "content"},
        )
        self.assertRedirects(response, "/login/")

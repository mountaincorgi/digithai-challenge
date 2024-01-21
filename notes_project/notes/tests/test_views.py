from django.test import TestCase


class NoteListTest(TestCase):
    def test_get_request_renders_the_note_list_template(self):
        pass

    def test_notes_ordered_from_newest_to_oldest(self):
        pass

    def test_user_cannot_see_other_users_notes(self):
        pass

    def test_user_must_be_logged_in_to_view_their_notes(self):
        pass

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        pass


class NoteListSearchTest(TestCase):
    def test_searching_by_exact_title_filters_notes_successfully(self):
        pass

    def test_searching_by_a_substring_filters_notes_successfully(self):
        pass

    def test_searching_is_not_case_sensitive(self):
        pass

    def test_searching_works_with_numbers(self):
        pass

    def test_searching_works_with_special_characters(self):
        pass

    def test_searching_strips_whitespace_from_the_search_term(self):
        pass

    def test_searching_returns_no_matches(self):
        pass

    def test_searching_with_a_blank_string_returns_all_notes(self):
        pass

    def test_searching_by_pk_does_not_work(self):
        pass

    def test_searching_by_content_does_not_work(self):
        pass

    def searching_returns_notes_ordered_from_newest_to_oldest(self):
        pass


class NoteCreateTest(TestCase):
    def test_get_request_renders_the_note_form_template(self):
        pass

    def test_user_can_create_their_own_note(self):
        pass

    def test_submitting_invalid_form_data_reloads_the_page(self):
        pass

    def test_user_cannot_create_notes_for_other_users(self):
        pass

    def test_user_must_be_logged_in_to_create_a_note(self):
        pass

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        pass


class NoteDetailTest(TestCase):
    def test_get_request_renders_the_note_detail_template(self):
        pass

    def test_user_can_read_their_own_note(self):
        pass

    def test_user_cannot_see_a_note_created_by_another_user(self):
        pass

    def test_user_must_be_logged_in_to_read_a_note(self):
        pass

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        pass


class NoteUpdateTest(TestCase):
    def test_get_request_renders_the_note_form_template(self):
        pass

    def test_user_can_update_their_own_note(self):
        pass

    def test_user_cannot_update_a_note_created_by_another_user(self):
        pass

    def test_user_must_be_logged_in_to_update_a_note(self):
        pass

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        pass


class NoteDeleteTest(TestCase):
    def test_get_request_renders_the_note_confirm_delete_template(self):
        pass

    def test_user_can_delete_their_own_note(self):
        pass

    def test_user_cannot_delete_a_note_created_by_another_user(self):
        pass

    def test_user_must_be_logged_in_to_delete_a_note(self):
        pass

    def test_unauthenticated_user_is_redirected_to_the_login_page(self):
        pass

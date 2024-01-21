from django.test import Client, TestCase
from users.factories import UserFactory


class SignUpTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_request_renders_the_sign_up_template(self):
        response = self.client.get("/sign-up/")
        self.assertTemplateUsed(response, "users/sign-up.html")

    def test_successfully_creating_a_user_redirects_to_the_login_page(self):
        response = self.client.post(
            "/sign-up/",
            {
                "username": "testuser",
                "password1": "abcd1234*",
                "password2": "abcd1234*",
            },
        )
        self.assertRedirects(response, "/login/")

    def test_failure_when_submitting_the_form_reloads_the_same_page(self):
        response = self.client.post(
            "/sign-up/",
            {
                "username": "testuser",
                "password1": "invalid",
                "password2": "invalid",
            },
        )
        self.assertTemplateUsed(response, "users/sign-up.html")


class LoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(username="testuser", password="abcd1234*")

    def test_get_request_renders_the_login_template(self):
        response = self.client.get("/login/")
        self.assertTemplateUsed(response, "users/login.html")

    def test_successfully_logging_in_redirects_to_the_notes_list_page(self):
        response = self.client.post(
            "/login/",
            {
                "username": "testuser",
                "password": "abcd1234*",
            },
        )
        self.assertRedirects(response, "/notes/")

    def test_failure_when_submitting_the_form_reloads_the_same_page(self):
        response = self.client.post(
            "/login/",
            {
                "username": "testuser",
                "password": "invalid",
            },
        )
        self.assertTemplateUsed(response, "users/login.html")


class LogoutTest(TestCase):
    def test_successfully_logging_out_redirects_to_the_login_page(self):
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/login/")

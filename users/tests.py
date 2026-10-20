from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

class AccountTests(TestCase):
    def test_registration_logs_user_in_and_shows_username(self):
        response = self.client.post(reverse("users:register"), {
            "username": "new_reader", "email": "reader@example.com",
            "password1": "MyLibrary!29847", "password2": "MyLibrary!29847",
        }, follow=True)
        self.assertRedirects(response, reverse("books:list"))
        self.assertTrue(get_user_model().objects.filter(username="new_reader").exists())
        self.assertContains(response, "new_reader")
        self.assertIn("_auth_user_id", self.client.session)

    def test_invalid_registration_does_not_create_user(self):
        response = self.client.post(reverse("users:register"), {
            "username": "reader", "password1": "123", "password2": "different",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_login_next_and_post_logout(self):
        user = get_user_model().objects.create_user("reader", password="Library!19372")
        response = self.client.post(reverse("users:login"), {
            "username": user.username, "password": "Library!19372", "next": reverse("books:add"),
        })
        self.assertRedirects(response, reverse("books:add"))
        self.assertEqual(self.client.get(reverse("users:logout")).status_code, 405)
        self.assertRedirects(self.client.post(reverse("users:logout")), reverse("books:home"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_does_not_redirect_to_external_site(self):
        get_user_model().objects.create_user("reader", password="Library!19372")
        response = self.client.post(reverse("users:login"), {
            "username": "reader", "password": "Library!19372", "next": "https://example.com/",
        })
        self.assertRedirects(response, reverse("books:list"))

    def test_wrong_password(self):
        get_user_model().objects.create_user("reader", password="Library!19372")
        response = self.client.post(reverse("users:login"), {"username": "reader", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)

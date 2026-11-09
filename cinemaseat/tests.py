from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginRoleRedirectTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.customer = self.user_model.objects.create_user(
            username='customer@example.com',
            email='customer@example.com',
            password='StrongPass123',
        )
        self.admin = self.user_model.objects.create_user(
            username='admin@example.com',
            email='admin@example.com',
            password='StrongPass123',
            is_staff=True,
            is_superuser=True,
        )

    def test_customer_login_redirects_to_customer_home(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'customer@example.com', 'password': 'StrongPass123', 'role': 'customer'},
            follow=True,
        )
        self.assertRedirects(response, reverse('home'))

    def test_admin_login_requires_staff_account(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'customer@example.com', 'password': 'StrongPass123', 'role': 'admin'},
            follow=True,
        )
        self.assertContains(response, 'Admin access only')

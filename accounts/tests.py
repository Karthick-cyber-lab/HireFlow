from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser, UserProfile


class AccountsAuthTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_applicant_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'newuser@hireflow.dev',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'applicant',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.filter(email='newuser@hireflow.dev').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'applicant')
        self.assertTrue(user.is_applicant)

    def test_recruiter_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'recruiter@hireflow.dev',
            'username': 'recruiter_hireflow',
            'first_name': 'Sarah',
            'last_name': 'Recruiter',
            'role': 'recruiter',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.filter(email='recruiter@hireflow.dev').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.role, 'recruiter')
        self.assertTrue(user.is_recruiter)

    def test_login_and_logout(self):
        user = CustomUser.objects.create_user(
            email='testlogin@hireflow.dev',
            username='testlogin',
            password='Password123!',
            role='applicant',
            first_name='Test',
            last_name='User'
        )
        login_res = self.client.post(reverse('accounts:login'), {
            'username': 'testlogin@hireflow.dev',
            'password': 'Password123!',
        })
        self.assertEqual(login_res.status_code, 302)

        logout_res = self.client.get(reverse('accounts:logout'))
        self.assertEqual(logout_res.status_code, 302)

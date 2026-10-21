import datetime
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import CustomUser
from jobs.models import Job, JobCategory
from applications.models import Application


class ApiEndpointTests(APITestCase):
    def setUp(self):
        self.recruiter = CustomUser.objects.create_user(
            email='recruiter@api.com',
            username='apirecruiter',
            password='Password123!',
            role='recruiter',
            first_name='API',
            last_name='Recruiter',
        )
        self.applicant = CustomUser.objects.create_user(
            email='applicant@api.com',
            username='apiapplicant',
            password='Password123!',
            role='applicant',
            first_name='API',
            last_name='Applicant',
        )
        self.category = JobCategory.objects.create(name='Mobile Dev', slug='mobile-dev')
        self.job = Job.objects.create(
            recruiter=self.recruiter,
            category=self.category,
            title='Flutter Engineer',
            company='MobileApps Inc',
            location='Remote',
            deadline=timezone.now().date() + datetime.timedelta(days=15),
            status='active',
            description='Build iOS and Android apps.',
            requirements='Flutter experience.',
        )

    def test_get_categories_list(self):
        url = reverse('api:category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(any(c['name'] == 'Mobile Dev' for c in results))

    def test_get_jobs_list(self):
        url = reverse('api:job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertTrue(any(j['title'] == 'Flutter Engineer' for j in results))

    def test_apply_via_api_and_prevent_duplicate(self):
        self.client.force_authenticate(user=self.applicant)
        url = reverse('api:application-list')

        # First apply
        res1 = self.client.post(url, {'job': self.job.pk, 'cover_letter': 'Hello World'})
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Duplicate apply fails
        res2 = self.client.post(url, {'job': self.job.pk, 'cover_letter': 'Second try'})
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recruiter_updates_status_via_api(self):
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            status='applied'
        )
        self.client.force_authenticate(user=self.recruiter)
        url = reverse('api:application-update-status', kwargs={'pk': app.pk})
        res = self.client.post(url, {'status': 'shortlisted', 'note': 'Approved via API'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, 'shortlisted')

    def test_dashboard_stats_api(self):
        self.client.force_authenticate(user=self.recruiter)
        url = reverse('api:stats-list')
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('total_jobs', res.data)
        self.assertIn('pipeline', res.data)

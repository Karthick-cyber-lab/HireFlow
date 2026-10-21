import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser
from jobs.models import Job, JobCategory


class JobModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.recruiter = CustomUser.objects.create_user(
            email='recruiter@test.com',
            username='testrecruiter',
            password='Password123!',
            role='recruiter',
            first_name='Sarah',
            last_name='Recruiter',
        )
        self.applicant = CustomUser.objects.create_user(
            email='applicant@test.com',
            username='testapplicant',
            password='Password123!',
            role='applicant',
            first_name='John',
            last_name='Applicant',
        )
        self.category = JobCategory.objects.create(
            name='Engineering',
            slug='engineering',
            icon='code-slash'
        )
        self.job = Job.objects.create(
            recruiter=self.recruiter,
            category=self.category,
            title='Django Backend Developer',
            company='Tech Solutions',
            location='Remote',
            job_type='remote',
            experience_level='mid',
            salary_min=100000,
            salary_max=150000,
            skills_required='Python, Django, PostgreSQL',
            deadline=timezone.now().date() + datetime.timedelta(days=30),
            status='active',
            description='We need a skilled backend engineer.',
            requirements='3+ years with Django.',
        )

    def test_job_list_view(self):
        response = self.client.get(reverse('jobs:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Backend Developer')

    def test_job_search(self):
        response = self.client.get(reverse('jobs:list'), {'q': 'Django'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Backend Developer')

        response_empty = self.client.get(reverse('jobs:list'), {'q': 'NonExistentSkillXYZ'})
        self.assertEqual(response_empty.status_code, 200)
        self.assertNotContains(response_empty, 'Django Backend Developer')

    def test_job_detail_and_view_count(self):
        initial_views = self.job.views_count
        response = self.client.get(reverse('jobs:detail', kwargs={'pk': self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.job.refresh_from_db()
        self.assertEqual(self.job.views_count, initial_views + 1)

    def test_recruiter_can_access_job_create(self):
        self.client.login(email='recruiter@test.com', password='Password123!')
        response = self.client.get(reverse('jobs:create'))
        self.assertEqual(response.status_code, 200)

    def test_applicant_cannot_access_job_create(self):
        self.client.login(email='applicant@test.com', password='Password123!')
        response = self.client.get(reverse('jobs:create'))
        # Should redirect or return 403 Forbidden
        self.assertIn(response.status_code, [302, 403])

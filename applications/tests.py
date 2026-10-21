import datetime
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import CustomUser, UserProfile
from jobs.models import Job, JobCategory
from applications.models import Application, Interview, StatusHistory


class ApplicationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.recruiter = CustomUser.objects.create_user(
            email='recruiter@test.com',
            username='testrecruiter',
            password='Password123!',
            role='recruiter',
            first_name='Recruiter',
            last_name='One',
        )
        self.applicant = CustomUser.objects.create_user(
            email='applicant@test.com',
            username='testapplicant',
            password='Password123!',
            role='applicant',
            first_name='Applicant',
            last_name='One',
        )
        self.applicant.profile.bio = 'Experienced developer'
        self.applicant.profile.save()

        self.category = JobCategory.objects.create(name='DevOps', slug='devops')
        self.job = Job.objects.create(
            recruiter=self.recruiter,
            category=self.category,
            title='Site Reliability Engineer',
            company='CloudNet',
            location='Remote',
            job_type='remote',
            salary_min=120000,
            skills_required='AWS, Docker, K8s',
            deadline=timezone.now().date() + datetime.timedelta(days=20),
            status='active',
            description='SRE needed.',
            requirements='K8s experience.',
        )

    def test_apply_for_job_and_duplicate_prevention(self):
        self.client.login(email='applicant@test.com', password='Password123!')

        # 1. First application succeeds
        response = self.client.post(
            reverse('applications:apply', kwargs={'job_pk': self.job.pk}),
            {'cover_letter': 'Excited to apply for this role!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Application.objects.filter(job=self.job, applicant=self.applicant).count(), 1)

        # Verify status history recorded
        app = Application.objects.get(job=self.job, applicant=self.applicant)
        self.assertEqual(app.status, 'applied')
        self.assertTrue(StatusHistory.objects.filter(application=app, to_status='applied').exists())

        # 2. Duplicate application is prevented
        dup_response = self.client.post(
            reverse('applications:apply', kwargs={'job_pk': self.job.pk}),
            {'cover_letter': 'Trying to apply a second time'}
        )
        self.assertEqual(dup_response.status_code, 302)
        self.assertEqual(Application.objects.filter(job=self.job, applicant=self.applicant).count(), 1)

    def test_recruiter_updates_status(self):
        # Create an initial application
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            status='applied',
            cover_letter='My application'
        )

        self.client.login(email='recruiter@test.com', password='Password123!')
        response = self.client.post(
            reverse('applications:update_status', kwargs={'pk': app.pk}),
            {'status': 'shortlisted', 'recruiter_notes': 'Great profile', 'note': 'Shortlisting for technical round'}
        )
        self.assertEqual(response.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, 'shortlisted')
        self.assertTrue(StatusHistory.objects.filter(application=app, to_status='shortlisted').exists())

    def test_applicant_withdraw_application(self):
        app = Application.objects.create(
            job=self.job,
            applicant=self.applicant,
            status='applied',
            cover_letter='My application'
        )

        self.client.login(email='applicant@test.com', password='Password123!')
        response = self.client.post(
            reverse('applications:withdraw', kwargs={'pk': app.pk})
        )
        self.assertEqual(response.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, 'withdrawn')

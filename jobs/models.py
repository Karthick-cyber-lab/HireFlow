from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='briefcase', help_text='Bootstrap icon name')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Job Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level (0-2 yrs)'),
        ('mid', 'Mid Level (2-5 yrs)'),
        ('senior', 'Senior Level (5+ yrs)'),
        ('lead', 'Lead / Manager'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('paused', 'Paused'),
    ]

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_jobs',
        limit_choices_to={'role__in': ['recruiter', 'admin']},
    )
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    location = models.CharField(max_length=150)
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='mid')
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True, help_text='Monthly salary in INR')
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    skills_required = models.TextField(help_text='Comma-separated skills')
    vacancies = models.PositiveIntegerField(default=1)
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f'{self.title} at {self.company}'

    def get_absolute_url(self):
        return reverse('jobs:detail', kwargs={'pk': self.pk})

    @property
    def is_expired(self):
        return self.deadline < timezone.now().date()

    @property
    def is_open(self):
        return self.status == 'active' and not self.is_expired

    def get_skills_list(self):
        return [s.strip() for s in self.skills_required.split(',') if s.strip()]

    def get_salary_display_str(self):
        if self.salary_min and self.salary_max:
            return f'₹{self.salary_min:,} - ₹{self.salary_max:,}/mo'
        elif self.salary_min:
            return f'₹{self.salary_min:,}+/mo'
        return 'Competitive'

    @property
    def application_count(self):
        return self.applications.count()

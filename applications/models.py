from django.db import models
from django.conf import settings
from jobs.models import Job


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('selected', 'Selected'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    STATUS_COLORS = {
        'applied': 'primary',
        'shortlisted': 'info',
        'interview': 'warning',
        'selected': 'success',
        'rejected': 'danger',
        'withdrawn': 'secondary',
    }

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    recruiter_notes = models.TextField(blank=True, help_text='Internal recruiter notes')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.applicant.get_full_name()} → {self.job.title}'

    def get_status_color(self):
        return self.STATUS_COLORS.get(self.status, 'secondary')

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

    def can_withdraw(self):
        return self.status in ['applied', 'shortlisted']


class Interview(models.Model):
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    MODE_CHOICES = [
        ('online', 'Online / Video Call'),
        ('phone', 'Phone'),
        ('in_person', 'In Person'),
        ('technical', 'Technical Round'),
        ('hr', 'HR Round'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='online')
    interviewer_name = models.CharField(max_length=100, blank=True)
    meeting_link = models.URLField(blank=True)
    venue = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f'Interview: {self.application} on {self.scheduled_at.strftime("%d %b %Y")}'


class StatusHistory(models.Model):
    """Track every status change for an application."""
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['changed_at']

    def __str__(self):
        return f'{self.application} | {self.from_status} → {self.to_status}'

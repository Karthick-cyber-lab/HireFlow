from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from datetime import timedelta
import csv
import io

from accounts.models import CustomUser, UserProfile
from jobs.models import Job, JobCategory
from applications.models import Application, Interview, StatusHistory


def role_required(*roles):
    """Decorator factory for role-based access."""
    from functools import wraps
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.conf import settings
                return redirect(settings.LOGIN_URL + f'?next={request.path}')
            if request.user.role not in roles:
                return HttpResponseForbidden('You do not have permission to access this page.')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


@login_required
def dashboard_home(request):
    """Route to the correct dashboard based on user role."""
    if request.user.is_admin:
        return redirect('dashboard:admin_overview')
    elif request.user.is_recruiter:
        return redirect('dashboard:recruiter_overview')
    else:
        return redirect('dashboard:applicant_overview')


# ─── RECRUITER DASHBOARD ────────────────────────────────────────────────────

@role_required('recruiter', 'admin')
def recruiter_overview(request):
    my_jobs = Job.objects.filter(recruiter=request.user).annotate(
        app_count=Count('applications')
    ).order_by('-created_at')

    total_applications = Application.objects.filter(job__recruiter=request.user).count()
    recent_applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related('applicant', 'job').order_by('-applied_at')[:10]

    pipeline = Application.objects.filter(
        job__recruiter=request.user
    ).values('status').annotate(count=Count('id'))
    pipeline_dict = {p['status']: p['count'] for p in pipeline}

    upcoming_interviews = Interview.objects.filter(
        application__job__recruiter=request.user,
        scheduled_at__gte=timezone.now(),
        result='pending',
    ).select_related('application__applicant', 'application__job').order_by('scheduled_at')[:5]

    return render(request, 'dashboard/recruiter/overview.html', {
        'my_jobs': my_jobs,
        'total_applications': total_applications,
        'recent_applications': recent_applications,
        'pipeline': pipeline_dict,
        'upcoming_interviews': upcoming_interviews,
        'active_jobs': my_jobs.filter(status='active').count(),
        'closed_jobs': my_jobs.filter(status='closed').count(),
    })


@role_required('recruiter', 'admin')
def recruiter_jobs(request):
    my_jobs = Job.objects.filter(recruiter=request.user).annotate(
        app_count=Count('applications'),
        selected_count=Count('applications', filter=Q(applications__status='selected')),
    ).order_by('-created_at')
    return render(request, 'dashboard/recruiter/jobs.html', {'my_jobs': my_jobs})


@role_required('recruiter', 'admin')
def recruiter_applicants(request):
    """View all applicants for recruiter's jobs with filtering."""
    job_filter = request.GET.get('job')
    status_filter = request.GET.get('status')

    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related('applicant', 'applicant__profile', 'job')

    if job_filter:
        applications = applications.filter(job_id=job_filter)
    if status_filter:
        applications = applications.filter(status=status_filter)

    my_jobs = Job.objects.filter(recruiter=request.user)
    status_choices = Application.STATUS_CHOICES

    return render(request, 'dashboard/recruiter/applicants.html', {
        'applications': applications,
        'my_jobs': my_jobs,
        'status_choices': status_choices,
        'selected_job': job_filter,
        'selected_status': status_filter,
    })


@role_required('recruiter', 'admin')
def recruiter_pipeline(request, job_pk):
    """Kanban-style pipeline view for a specific job."""
    job = get_object_or_404(Job, pk=job_pk, recruiter=request.user)
    statuses = ['applied', 'shortlisted', 'interview', 'selected', 'rejected']
    pipeline = {
        s: Application.objects.filter(job=job, status=s).select_related('applicant', 'applicant__profile')
        for s in statuses
    }
    return render(request, 'dashboard/recruiter/pipeline.html', {
        'job': job,
        'pipeline': pipeline,
        'status_choices': Application.STATUS_CHOICES,
    })


# ─── APPLICANT DASHBOARD ─────────────────────────────────────────────────────

@role_required('applicant')
def applicant_overview(request):
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__category')

    upcoming_interviews = Interview.objects.filter(
        application__applicant=request.user,
        scheduled_at__gte=timezone.now(),
        result='pending',
    ).select_related('application__job').order_by('scheduled_at')[:3]

    status_counts = {
        s: applications.filter(status=s).count()
        for s, _ in Application.STATUS_CHOICES
    }

    return render(request, 'dashboard/applicant/overview.html', {
        'applications': applications[:10],
        'total_applications': applications.count(),
        'upcoming_interviews': upcoming_interviews,
        'status_counts': status_counts,
    })


# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────

@role_required('admin')
def admin_overview(request):
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)

    stats = {
        'total_users': CustomUser.objects.count(),
        'total_applicants': CustomUser.objects.filter(role='applicant').count(),
        'total_recruiters': CustomUser.objects.filter(role='recruiter').count(),
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(status='active').count(),
        'total_applications': Application.objects.count(),
        'selected_count': Application.objects.filter(status='selected').count(),
        'this_month_apps': Application.objects.filter(applied_at__gte=thirty_days_ago).count(),
        'this_month_jobs': Job.objects.filter(created_at__gte=thirty_days_ago).count(),
    }

    # Applications by status (for chart)
    app_by_status = list(Application.objects.values('status').annotate(count=Count('id')))
    # Jobs by category (for chart)
    jobs_by_category = list(
        JobCategory.objects.annotate(job_count=Count('jobs')).values('name', 'job_count')
    )
    # Recent activity
    recent_apps = Application.objects.select_related('applicant', 'job').order_by('-applied_at')[:10]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]

    return render(request, 'dashboard/admin/overview.html', {
        'stats': stats,
        'app_by_status': app_by_status,
        'jobs_by_category': jobs_by_category,
        'recent_apps': recent_apps,
        'recent_users': recent_users,
    })


@role_required('admin')
def admin_users(request):
    role_filter = request.GET.get('role', '')
    search = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    if role_filter:
        users = users.filter(role=role_filter)
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    return render(request, 'dashboard/admin/users.html', {
        'users': users, 'role_filter': role_filter, 'search': search,
    })


@role_required('admin')
def admin_toggle_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.email} {status}.')
    return redirect('dashboard:admin_users')


@role_required('admin')
def admin_jobs(request):
    jobs = Job.objects.select_related('recruiter', 'category').annotate(
        app_count=Count('applications')
    ).order_by('-created_at')
    return render(request, 'dashboard/admin/jobs.html', {'jobs': jobs})


# ─── CSV EXPORT ──────────────────────────────────────────────────────────────

@role_required('admin', 'recruiter')
def export_applications_csv(request):
    if request.user.is_admin:
        applications = Application.objects.all()
    else:
        applications = Application.objects.filter(job__recruiter=request.user)

    job_filter = request.GET.get('job')
    status_filter = request.GET.get('status')
    if job_filter:
        applications = applications.filter(job_id=job_filter)
    if status_filter:
        applications = applications.filter(status=status_filter)

    applications = applications.select_related('applicant', 'job')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="applications_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Applicant Name', 'Email', 'Job Title', 'Company',
        'Status', 'Applied Date', 'Updated Date', 'Cover Letter',
    ])
    for app in applications:
        writer.writerow([
            app.applicant.get_full_name(),
            app.applicant.email,
            app.job.title,
            app.job.company,
            app.get_status_display(),
            app.applied_at.strftime('%Y-%m-%d %H:%M'),
            app.updated_at.strftime('%Y-%m-%d %H:%M'),
            app.cover_letter[:200] if app.cover_letter else '',
        ])

    return response


@role_required('admin')
def export_jobs_csv(request):
    jobs = Job.objects.select_related('recruiter', 'category').annotate(
        app_count=Count('applications')
    )
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="jobs_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Company', 'Category', 'Type', 'Location',
        'Status', 'Deadline', 'Applications', 'Posted By', 'Created At',
    ])
    for job in jobs:
        writer.writerow([
            job.title, job.company,
            job.category.name if job.category else '',
            job.get_job_type_display(), job.location,
            job.get_status_display(),
            job.deadline.strftime('%Y-%m-%d'),
            job.app_count,
            job.recruiter.email,
            job.created_at.strftime('%Y-%m-%d'),
        ])
    return response

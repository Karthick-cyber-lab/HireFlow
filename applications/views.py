from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from jobs.models import Job
from .models import Application, Interview, StatusHistory
from .forms import ApplicationForm, StatusUpdateForm, InterviewForm
from accounts.models import UserProfile


def recruiter_or_admin_required(view_func):
    """Decorator: only recruiter or admin can access."""
    from functools import wraps
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_recruiter or request.user.is_admin):
            return HttpResponseForbidden('Access denied.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
def apply_job(request, job_pk):
    if not request.user.is_applicant:
        messages.error(request, 'Only applicants can apply for jobs.')
        return redirect('jobs:detail', pk=job_pk)

    job = get_object_or_404(Job, pk=job_pk, status='active')

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:detail', pk=job_pk)

    if job.is_expired:
        messages.error(request, 'This job posting has expired.')
        return redirect('jobs:detail', pk=job_pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            # Use profile resume if no resume uploaded
            if not application.resume:
                try:
                    profile = request.user.profile
                    if profile.resume:
                        application.resume = profile.resume
                except Exception:
                    pass
            application.save()
            StatusHistory.objects.create(
                application=application,
                from_status='',
                to_status='applied',
                changed_by=request.user,
                note='Application submitted.',
            )
            messages.success(request, f'Successfully applied for {job.title}!')
            return redirect('applications:my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'applications/apply.html', {'job': job, 'form': form})


@login_required
def my_applications(request):
    if not request.user.is_applicant:
        return redirect('dashboard:home')
    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__category', 'job__recruiter')
    return render(request, 'applications/my_applications.html', {'applications': applications})


@login_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    # Allow applicant who owns it or recruiter of the job or admin
    if not (
        application.applicant == request.user or
        application.job.recruiter == request.user or
        request.user.is_admin
    ):
        return HttpResponseForbidden('Access denied.')

    interviews = application.interviews.all()
    history = application.history.all()
    return render(request, 'applications/application_detail.html', {
        'application': application,
        'interviews': interviews,
        'history': history,
    })


@login_required
def withdraw_application(request, pk):
    application = get_object_or_404(Application, pk=pk, applicant=request.user)
    if not application.can_withdraw():
        messages.error(request, 'This application cannot be withdrawn at this stage.')
        return redirect('applications:my_applications')

    if request.method == 'POST':
        old_status = application.status
        application.status = 'withdrawn'
        application.save()
        StatusHistory.objects.create(
            application=application,
            from_status=old_status,
            to_status='withdrawn',
            changed_by=request.user,
            note='Application withdrawn by applicant.',
        )
        messages.success(request, 'Application withdrawn.')
        return redirect('applications:my_applications')

    return render(request, 'applications/confirm_withdraw.html', {'application': application})


@recruiter_or_admin_required
def update_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    if application.job.recruiter != request.user and not request.user.is_admin:
        return HttpResponseForbidden('Access denied.')

    if request.method == 'POST':
        form = StatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            old_status = application.status
            app = form.save(commit=False)
            note = form.cleaned_data.get('note', '')
            app.save()
            StatusHistory.objects.create(
                application=app,
                from_status=old_status,
                to_status=app.status,
                changed_by=request.user,
                note=note,
            )
            messages.success(request, f'Application status updated to {app.get_status_display()}.')
            return redirect('applications:detail', pk=pk)
    else:
        form = StatusUpdateForm(instance=application)

    return render(request, 'applications/update_status.html', {'form': form, 'application': application})


@recruiter_or_admin_required
def schedule_interview(request, application_pk):
    application = get_object_or_404(Application, pk=application_pk)
    if application.job.recruiter != request.user and not request.user.is_admin:
        return HttpResponseForbidden('Access denied.')

    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
            # Auto-update application status to interview
            if application.status not in ['selected', 'rejected']:
                old_status = application.status
                application.status = 'interview'
                application.save()
                StatusHistory.objects.create(
                    application=application,
                    from_status=old_status,
                    to_status='interview',
                    changed_by=request.user,
                    note=f'Interview scheduled for {interview.scheduled_at.strftime("%d %b %Y %H:%M")}.',
                )
            messages.success(request, 'Interview scheduled successfully!')
            return redirect('applications:detail', pk=application_pk)
    else:
        form = InterviewForm()

    return render(request, 'applications/schedule_interview.html', {
        'form': form,
        'application': application,
    })

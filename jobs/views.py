from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Job, JobCategory
from .forms import JobForm, JobSearchForm
from accounts.models import UserProfile


def job_list(request):
    """Public job listing with search & filter."""
    jobs = Job.objects.filter(status='active').select_related('category', 'recruiter')
    form = JobSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')
        location = form.cleaned_data.get('location')
        experience = form.cleaned_data.get('experience')

        if q:
            jobs = jobs.filter(
                Q(title__icontains=q) |
                Q(company__icontains=q) |
                Q(skills_required__icontains=q) |
                Q(description__icontains=q)
            )
        if category:
            jobs = jobs.filter(category=category)
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        if location:
            jobs = jobs.filter(location__icontains=location)
        if experience:
            jobs = jobs.filter(experience_level=experience)

    featured = jobs.filter(is_featured=True)[:4]
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = JobCategory.objects.all()

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj,
        'form': form,
        'categories': categories,
        'featured': featured,
        'total_jobs': jobs.count(),
    })


def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    # Increment view count
    Job.objects.filter(pk=pk).update(views_count=job.views_count + 1)

    already_applied = False
    if request.user.is_authenticated and request.user.is_applicant:
        already_applied = job.applications.filter(applicant=request.user).exists()

    similar_jobs = Job.objects.filter(
        category=job.category, status='active'
    ).exclude(pk=pk)[:4]

    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'already_applied': already_applied,
        'similar_jobs': similar_jobs,
    })


@login_required
def job_create(request):
    if not (request.user.is_recruiter or request.user.is_admin):
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('jobs:list')

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm()

    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Post a Job'})


@login_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.recruiter != request.user and not request.user.is_admin:
        messages.error(request, 'You do not have permission to edit this job.')
        return redirect('jobs:detail', pk=pk)

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs:detail', pk=pk)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_form.html', {'form': form, 'title': 'Edit Job', 'job': job})


@login_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.recruiter != request.user and not request.user.is_admin:
        messages.error(request, 'You do not have permission to delete this job.')
        return redirect('jobs:detail', pk=pk)

    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Job "{title}" deleted.')
        return redirect('dashboard:recruiter_jobs')

    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


def category_jobs(request, slug):
    category = get_object_or_404(JobCategory, slug=slug)
    jobs = Job.objects.filter(category=category, status='active')
    paginator = Paginator(jobs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'jobs/category_jobs.html', {'category': category, 'page_obj': page_obj})

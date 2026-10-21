from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    # Recruiter
    path('recruiter/', views.recruiter_overview, name='recruiter_overview'),
    path('recruiter/jobs/', views.recruiter_jobs, name='recruiter_jobs'),
    path('recruiter/applicants/', views.recruiter_applicants, name='recruiter_applicants'),
    path('recruiter/pipeline/<int:job_pk>/', views.recruiter_pipeline, name='recruiter_pipeline'),
    # Applicant
    path('applicant/', views.applicant_overview, name='applicant_overview'),
    # Admin
    path('admin-panel/', views.admin_overview, name='admin_overview'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:pk>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-panel/jobs/', views.admin_jobs, name='admin_jobs'),
    # Exports
    path('export/applications/', views.export_applications_csv, name='export_applications'),
    path('export/jobs/', views.export_jobs_csv, name='export_jobs'),
]

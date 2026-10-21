from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('jobs/<int:pk>/', views.job_detail, name='detail'),
    path('jobs/create/', views.job_create, name='create'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='delete'),
    path('category/<slug:slug>/', views.category_jobs, name='category'),
]

from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_pk>/', views.apply_job, name='apply'),
    path('my/', views.my_applications, name='my_applications'),
    path('<int:pk>/', views.application_detail, name='detail'),
    path('<int:pk>/withdraw/', views.withdraw_application, name='withdraw'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
    path('<int:application_pk>/interview/', views.schedule_interview, name='schedule_interview'),
]

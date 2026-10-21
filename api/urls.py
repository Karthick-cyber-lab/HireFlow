from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register('jobs', views.JobViewSet, basename='job')
router.register('categories', views.JobCategoryViewSet, basename='category')
router.register('applications', views.ApplicationViewSet, basename='application')
router.register('interviews', views.InterviewViewSet, basename='interview')
router.register('stats', views.DashboardStatsViewSet, basename='stats')
router.register('admin/users', views.AdminUserViewSet, basename='admin-user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]

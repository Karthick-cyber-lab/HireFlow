from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import CustomUser, UserProfile
from jobs.models import Job, JobCategory
from applications.models import Application, Interview, StatusHistory
from .serializers import (
    UserSerializer, JobCategorySerializer,
    JobListSerializer, JobDetailSerializer, JobCreateUpdateSerializer,
    ApplicationSerializer, InterviewSerializer, DashboardStatsSerializer,
)


class IsRecruiterOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['recruiter', 'admin']


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class JobCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = JobCategory.objects.annotate(job_count=Count('jobs')).all().order_by('name')
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.AllowAny]


class JobViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'job_type', 'experience_level', 'category']
    search_fields = ['title', 'company', 'skills_required', 'location']
    ordering_fields = ['created_at', 'deadline', 'views_count']

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role in ['recruiter', 'admin']:
            if self.request.user.role == 'admin':
                return Job.objects.all().select_related('category', 'recruiter')
            return Job.objects.filter(recruiter=self.request.user).select_related('category', 'recruiter')
        return Job.objects.filter(status='active').select_related('category', 'recruiter')

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return JobCreateUpdateSerializer
        return JobDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRecruiterOrAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.recruiter == request.user


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Application.objects.all().select_related('applicant', 'job')
        if user.role == 'recruiter':
            return Application.objects.filter(job__recruiter=user).select_related('applicant', 'job')
        return Application.objects.filter(applicant=user).select_related('job')

    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        if Application.objects.filter(job=job, applicant=self.request.user).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError('You have already applied for this job.')
        app = serializer.save(applicant=self.request.user)
        StatusHistory.objects.create(
            application=app, from_status='', to_status='applied',
            changed_by=self.request.user, note='Application submitted via API.'
        )

    @action(detail=True, methods=['post'], permission_classes=[IsRecruiterOrAdmin])
    def update_status(self, request, pk=None):
        application = self.get_object()
        new_status = request.data.get('status')
        note = request.data.get('note', '')
        valid_statuses = [s for s, _ in Application.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        old_status = application.status
        application.status = new_status
        application.save()
        StatusHistory.objects.create(
            application=application, from_status=old_status, to_status=new_status,
            changed_by=request.user, note=note
        )
        return Response({'status': new_status, 'message': 'Status updated.'})


class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = [IsRecruiterOrAdmin]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Interview.objects.all()
        return Interview.objects.filter(application__job__recruiter=self.request.user)


class DashboardStatsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        if user.role == 'recruiter':
            jobs_qs = Job.objects.filter(recruiter=user)
            apps_qs = Application.objects.filter(job__recruiter=user)
        elif user.role == 'admin':
            jobs_qs = Job.objects.all()
            apps_qs = Application.objects.all()
        else:
            apps_qs = Application.objects.filter(applicant=user)
            pipeline = {s: apps_qs.filter(status=s).count() for s, _ in Application.STATUS_CHOICES}
            return Response({'total_applications': apps_qs.count(), 'pipeline': pipeline})

        pipeline = {s: apps_qs.filter(status=s).count() for s, _ in Application.STATUS_CHOICES}
        data = {
            'total_jobs': jobs_qs.count(),
            'active_jobs': jobs_qs.filter(status='active').count(),
            'total_applications': apps_qs.count(),
            'pipeline': pipeline,
        }
        return Response(data)


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'first_name', 'last_name', 'role']

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'is_active': user.is_active})

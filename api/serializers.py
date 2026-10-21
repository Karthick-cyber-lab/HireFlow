from rest_framework import serializers
from accounts.models import CustomUser, UserProfile
from jobs.models import Job, JobCategory
from applications.models import Application, Interview


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'location', 'skills', 'experience_years', 'linkedin_url']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'full_name', 'profile']

    def get_full_name(self, obj):
        return obj.get_full_name()


class JobCategorySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'slug', 'icon', 'job_count']


class JobListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    recruiter_name = serializers.CharField(source='recruiter.get_full_name', read_only=True)
    salary_display = serializers.CharField(source='get_salary_display_str', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    application_count = serializers.IntegerField(read_only=True)
    skills_list = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location', 'job_type', 'experience_level',
            'category_name', 'recruiter_name', 'salary_display', 'skills_list',
            'deadline', 'status', 'is_featured', 'is_open', 'application_count',
            'views_count', 'created_at',
        ]

    def get_skills_list(self, obj):
        return obj.get_skills_list()


class JobDetailSerializer(JobListSerializer):
    class Meta(JobListSerializer.Meta):
        fields = JobListSerializer.Meta.fields + ['description', 'requirements', 'responsibilities', 'vacancies']


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'company', 'location', 'job_type', 'experience_level',
            'description', 'requirements', 'responsibilities',
            'salary_min', 'salary_max', 'skills_required', 'vacancies', 'deadline', 'status',
        ]

    def create(self, validated_data):
        validated_data['recruiter'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    company = serializers.CharField(source='job.company', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'job_title', 'company', 'applicant', 'applicant_name',
            'status', 'status_display', 'status_color',
            'cover_letter', 'applied_at', 'updated_at',
        ]
        read_only_fields = ['applicant', 'applied_at', 'updated_at']


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'scheduled_at', 'duration_minutes', 'mode',
            'interviewer_name', 'meeting_link', 'venue', 'notes', 'result', 'feedback',
        ]


class DashboardStatsSerializer(serializers.Serializer):
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    pipeline = serializers.DictField(child=serializers.IntegerField())

from django.contrib import admin
from .models import Job, JobCategory


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'recruiter', 'category', 'job_type', 'status',
                    'deadline', 'application_count', 'views_count', 'created_at')
    list_filter = ('status', 'job_type', 'experience_level', 'category', 'is_featured')
    search_fields = ('title', 'company', 'description')
    raw_id_fields = ('recruiter',)
    date_hierarchy = 'created_at'
    actions = ['make_active', 'make_closed']

    def make_active(self, request, queryset):
        queryset.update(status='active')
    make_active.short_description = 'Mark selected jobs as Active'

    def make_closed(self, request, queryset):
        queryset.update(status='closed')
    make_closed.short_description = 'Mark selected jobs as Closed'

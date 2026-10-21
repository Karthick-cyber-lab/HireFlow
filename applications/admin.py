from django.contrib import admin
from .models import Application, Interview, StatusHistory


class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0
    fields = ('scheduled_at', 'mode', 'interviewer_name', 'result')


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'note', 'changed_at')
    can_delete = False


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'job__category')
    search_fields = ('applicant__email', 'applicant__first_name', 'job__title', 'job__company')
    raw_id_fields = ('applicant', 'job')
    inlines = [InterviewInline, StatusHistoryInline]
    date_hierarchy = 'applied_at'


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_at', 'mode', 'result')
    list_filter = ('mode', 'result')
    search_fields = ('application__applicant__email', 'application__job__title')

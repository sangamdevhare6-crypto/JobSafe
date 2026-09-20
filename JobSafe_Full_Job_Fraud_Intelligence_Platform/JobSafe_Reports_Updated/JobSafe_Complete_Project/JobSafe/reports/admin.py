from django.contrib import admin
from .models import ScamReport

@admin.register(ScamReport)
class ScamReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'company', 'job_title', 'scam_type', 'status', 'user', 'created_at')
    list_filter = ('status', 'scam_type', 'created_at')
    search_fields = ('company', 'job_title', 'recruiter_name', 'recruiter_contact', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

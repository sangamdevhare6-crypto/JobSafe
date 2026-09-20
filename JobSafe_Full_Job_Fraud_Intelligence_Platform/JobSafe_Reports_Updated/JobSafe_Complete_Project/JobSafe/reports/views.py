from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, render, redirect
from .models import ScamReport

@login_required
def scam_reports(request):
    if request.method == 'POST':
        ScamReport.objects.create(
            user=request.user,
            company=request.POST.get('company', '').strip(),
            job_title=request.POST.get('job_title', '').strip(),
            recruiter_name=request.POST.get('recruiter_name', '').strip(),
            recruiter_contact=request.POST.get('recruiter_contact', '').strip(),
            job_url=request.POST.get('job_url', '').strip(),
            scam_type=request.POST.get('scam_type', 'Other'),
            payment_requested=request.POST.get('payment_requested', '').strip(),
            evidence_url=request.POST.get('evidence_url', '').strip(),
            description=request.POST.get('description', '').strip(),
        )
        messages.success(request, 'Your scam report has been submitted for review.')
        return redirect('scam_reports')

    reports = ScamReport.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'scam-reports.html', {
        'reports': reports,
        'scam_types': ScamReport.SCAM_TYPES,
        'active': 'reports',
    })


def _is_staff(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(_is_staff, login_url='/admin-login/')
def admin_reports(request):
    if request.method == 'POST':
        report = get_object_or_404(ScamReport, pk=request.POST.get('report_id'))
        action = request.POST.get('action')
        note = request.POST.get('admin_note', '').strip()
        if action in dict(ScamReport.STATUS_CHOICES):
            report.status = action
            if note:
                report.admin_note = note
            report.save(update_fields=['status', 'admin_note', 'updated_at'])
            messages.success(request, f'Report #{report.id} updated to {report.status}.')
        return redirect('admin_reports')

    status = request.GET.get('status', '').strip()
    reports = ScamReport.objects.select_related('user').order_by('-created_at')
    if status in dict(ScamReport.STATUS_CHOICES):
        reports = reports.filter(status=status)

    counts = {key: ScamReport.objects.filter(status=key).count() for key, _ in ScamReport.STATUS_CHOICES}
    return render(request, 'admin-reports.html', {
        'reports': reports,
        'counts': counts,
        'pending_count': counts['Pending'],
        'review_count': counts['Under Review'],
        'verified_count': counts['Verified Scam'],
        'rejected_count': counts['Rejected'],
        'statuses': ScamReport.STATUS_CHOICES,
        'active': 'reports',
        'current_status': status,
    })

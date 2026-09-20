from django.db import models
from django.contrib.auth.models import User

class ScamReport(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Verified Scam', 'Verified Scam'),
        ('Rejected', 'Rejected'),
    ]
    SCAM_TYPES = [
        ('Registration Fee', 'Registration Fee'),
        ('Fake Recruiter', 'Fake Recruiter'),
        ('Fake Job Offer', 'Fake Job Offer'),
        ('WhatsApp/Telegram Scam', 'WhatsApp/Telegram Scam'),
        ('Fake Website', 'Fake Website'),
        ('Credential Theft', 'Credential Theft'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scam_reports')
    company = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    recruiter_name = models.CharField(max_length=200, blank=True)
    recruiter_contact = models.CharField(max_length=200, blank=True)
    job_url = models.URLField(blank=True)
    scam_type = models.CharField(max_length=60, choices=SCAM_TYPES, default='Other')
    payment_requested = models.CharField(max_length=100, blank=True)
    evidence_url = models.URLField(blank=True)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.company} - {self.job_title}'

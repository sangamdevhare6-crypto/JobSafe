from django.db import models
from django.contrib.auth.models import User


class JobCheck(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    company = models.CharField(
        max_length=200,
        blank=True
    )

    source = models.CharField(
        max_length=100,
        blank=True
    )

    url = models.URLField(
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    risk_score = models.PositiveIntegerField(
        default=0
    )

    risk_level = models.CharField(
        max_length=30,
        default="Safe"
    )

    reasons = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.risk_score}/100"


class CompanyCheck(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="company_checks"
    )

    company = models.CharField(
        max_length=200
    )

    website = models.URLField(
        blank=True
    )

    domain = models.CharField(
        max_length=200,
        blank=True
    )

    risk_score = models.IntegerField(
        default=0
    )

    status = models.CharField(
        max_length=30,
        default="Low Risk"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.company} - {self.user.username}"
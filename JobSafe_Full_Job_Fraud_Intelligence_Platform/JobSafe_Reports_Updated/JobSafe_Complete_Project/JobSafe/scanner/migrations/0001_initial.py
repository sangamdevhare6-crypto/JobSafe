from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [

        migrations.CreateModel(
            name="JobCheck",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=200),
                ),
                (
                    "company",
                    models.CharField(
                        max_length=200,
                        blank=True,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        max_length=100,
                        blank=True,
                    ),
                ),
                (
                    "url",
                    models.URLField(blank=True),
                ),
                (
                    "description",
                    models.TextField(blank=True),
                ),
                (
                    "risk_score",
                    models.PositiveIntegerField(default=0),
                ),
                (
                    "risk_level",
                    models.CharField(
                        max_length=30,
                        default="Safe",
                    ),
                ),
                (
                    "reasons",
                    models.TextField(blank=True),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="auth.user",
                    ),
                ),
            ],
        ),

        migrations.CreateModel(
            name="CompanyCheck",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "company",
                    models.CharField(max_length=200),
                ),
                (
                    "website",
                    models.URLField(blank=True),
                ),
                (
                    "domain",
                    models.CharField(
                        max_length=200,
                        blank=True,
                    ),
                ),
                (
                    "risk_score",
                    models.IntegerField(default=0),
                ),
                (
                    "status",
                    models.CharField(
                        max_length=30,
                        default="Low Risk",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="company_checks",
                        to="auth.user",
                    ),
                ),
            ],
        ),
    ]
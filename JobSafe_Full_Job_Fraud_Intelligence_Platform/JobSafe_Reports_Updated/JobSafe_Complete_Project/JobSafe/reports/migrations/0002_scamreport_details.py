from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('reports', '0001_initial')]
    operations = [
        migrations.AddField(model_name='scamreport', name='recruiter_name', field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name='scamreport', name='recruiter_contact', field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name='scamreport', name='job_url', field=models.URLField(blank=True)),
        migrations.AddField(model_name='scamreport', name='scam_type', field=models.CharField(choices=[('Registration Fee','Registration Fee'),('Fake Recruiter','Fake Recruiter'),('Fake Job Offer','Fake Job Offer'),('WhatsApp/Telegram Scam','WhatsApp/Telegram Scam'),('Fake Website','Fake Website'),('Credential Theft','Credential Theft'),('Other','Other')], default='Other', max_length=60)),
        migrations.AddField(model_name='scamreport', name='payment_requested', field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name='scamreport', name='evidence_url', field=models.URLField(blank=True)),
        migrations.AddField(model_name='scamreport', name='admin_note', field=models.TextField(blank=True)),
        migrations.AddField(model_name='scamreport', name='updated_at', field=models.DateTimeField(auto_now=True)),
        migrations.AlterField(model_name='scamreport', name='status', field=models.CharField(choices=[('Pending','Pending'),('Under Review','Under Review'),('Verified Scam','Verified Scam'),('Rejected','Rejected')], default='Pending', max_length=30)),
    ]

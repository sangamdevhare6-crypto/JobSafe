# JobSafe — Full Job Fraud Intelligence & Protection Platform

JobSafe is a Django-based job-scam protection platform with user scanning, company intelligence, evidence scanning, scam reporting and an administrator command center.

## Included modules

### User
- Dashboard
- AI Job Scanner
- Company Intelligence
- Screenshot / Evidence Scanner
- Scan History
- Risk Analytics
- Threat Center
- Alerts
- Scam Reports
- Evidence Vault
- Safety Center
- Resources
- Profile
- Security Settings

### Admin
- Dashboard
- Platform Analytics
- Threat Intelligence
- User Management
- Scam Reports Review
- Company Intelligence
- Audit Logs
- System Monitor
- Django Admin

## Run

```powershell
cd JobSafe
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```            

Open `http://127.0.0.1:8000/`.

## Database migration repair

The scanner model now uses `domain` consistently. Migration `0001_initial.py` creates `domain`, and the old `0002` rename migration is intentionally a no-op so existing databases that already applied it remain compatible.

If your old database still reports `no such column: scanner_companycheck.email_domain`, make sure you are running this project's `manage.py` and the current `scanner/models.py`, then run:

```powershell
python manage.py migrate
python manage.py check
```

Do not delete `db.sqlite3` if you need to preserve existing records.

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests

from scanner.models import JobCheck, CompanyCheck
from reports.models import ScamReport
from .forms import SignupForm


def home(request):
    if request.user.is_authenticated:
        return redirect(
            "admin_dashboard"
            if request.user.is_staff
            else "dashboard"
        )

    return render(request, "home.html")


def _do_login(request, admin_only=False):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user and (not admin_only or user.is_staff):

            login(request, user)

            return redirect(
                "admin_dashboard"
                if user.is_staff
                else "dashboard"
            )

        messages.error(
            request,
            "Invalid credentials or admin access required."
        )

    return render(
        request,
        "admin-login.html"
        if admin_only
        else "login.html"
    )


def login_view(request):
    return _do_login(request, False)


def admin_login(request):
    return _do_login(request, True)


def signup(request):

    if request.method == "POST":

        form = SignupForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("dashboard")

    else:

        form = SignupForm()

    return render(
        request,
        "signup.html",
        {"form": form}
    )


def logout_view(request):

    logout(request)

    return redirect("login")


@login_required
def dashboard(request):

    checks = (
        JobCheck.objects
        .filter(user=request.user)
        .order_by("-created_at")[:5]
    )

    total = JobCheck.objects.filter(
        user=request.user
    ).count()

    safe = JobCheck.objects.filter(
        user=request.user,
        risk_level="Safe"
    ).count()

    suspicious = JobCheck.objects.filter(
        user=request.user,
        risk_level="Suspicious"
    ).count()

    high = JobCheck.objects.filter(
        user=request.user,
        risk_level="High Risk"
    ).count()

    reports = ScamReport.objects.filter(
        user=request.user
    ).count()

    return render(
        request,
        "dashboard.html",
        {
            "checks": checks,
            "total": total,
            "safe": safe,
            "suspicious": suspicious,
            "high": high,
            "reports": reports,
            "active": "dashboard"
        }
    )


@user_passes_test(
    lambda u: u.is_staff,
    login_url="/admin-login/"
)
def admin_dashboard(request):

    recent_company_checks = (
        CompanyCheck.objects
        .select_related("user")
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "admin-dashboard.html",
        {
            "users": User.objects.count(),
            "checks": JobCheck.objects.count(),
            "reports": ScamReport.objects.count(),
            "companies": CompanyCheck.objects.count(),
            "recent_reports": (
                ScamReport.objects
                .order_by("-created_at")[:6]
            ),
            "recent_company_checks": recent_company_checks
        }
    )


@user_passes_test(
    lambda u: u.is_staff,
    login_url="/admin-login/"
)
def admin_users(request):

    return render(
        request,
        "admin-users.html",
        {
            "users": User.objects
            .all()
            .order_by("-date_joined")
        }
    )


@user_passes_test(
    lambda u: u.is_staff,
    login_url="/admin-login/"
)
def admin_companies(request):

    companies = (
        CompanyCheck.objects
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "admin-companies.html",
        {
            "companies": companies
        }
    )


@login_required
def safety_guide(request):

    return render(
        request,
        "safety-guide.html"
    )


@login_required
def company_check(request):

    company = ""
    website = ""
    domain = ""
    result = None

    if request.method == "POST":

        company = request.POST.get(
            "company",
            ""
        ).strip()

        website = request.POST.get(
            "website",
            ""
        ).strip()

        domain = request.POST.get(
            "domain",
            ""
        ).strip()

        risk = 0
        reasons = []

        if not company:

            messages.error(
                request,
                "Please enter a company name."
            )

            return render(
                request,
                "company-check.html",
                {
                    "company": company,
                    "website": website,
                    "domain": domain,
                    "result": None
                }
            )

        if not website:

            risk += 20

            reasons.append(
                "Official website was not provided."
            )

        if website:

            website_lower = website.lower()

            if not (
                website_lower.startswith("http://")
                or website_lower.startswith("https://")
            ):

                risk += 10

                reasons.append(
                    "Website does not use a standard HTTP/HTTPS URL."
                )

        if not domain:

            risk += 20

            reasons.append(
                "Recruiter email domain was not provided."
            )

        if domain:

            domain_lower = domain.lower()

            free_email_domains = [
                "gmail.com",
                "yahoo.com",
                "outlook.com",
                "hotmail.com",
                "proton.me",
                "protonmail.com"
            ]

            if any(
                free_domain in domain_lower
                for free_domain in free_email_domains
            ):

                risk += 35

                reasons.append(
                    "Recruiter contact appears to use a free email provider instead of a company domain."
                )

        risk = min(risk, 100)

        if risk >= 60:

            status = "High Risk"

        elif risk >= 30:

            status = "Suspicious"

        else:

            status = "Low Risk"

        company_record = CompanyCheck.objects.create(
            user=request.user,
            company=company,
            website=website,
            domain=domain,
            risk_score=risk,
            status=status
        )

        result = {
            "status": status,
            "risk": risk,
            "company": company,
            "website": website,
            "domain": domain,
            "reasons": reasons,
            "check_id": company_record.id
        }

    elif request.method == "GET":

        company = request.GET.get(
            "company",
            ""
        ).strip()

    return render(
        request,
        "company-check.html",
        {
            "company": company,
            "website": website,
            "domain": domain,
            "result": result
        }
    )


def company_search_api(request):

    query = request.GET.get(
        "q",
        ""
    ).strip()

    if not query:

        return JsonResponse({
            "success": False,
            "results": []
        })

    try:

        url = "https://www.wikidata.org/w/api.php"

        params = {
            "action": "wbsearchentities",
            "search": query,
            "language": "en",
            "format": "json",
            "limit": 8,
            "type": "item"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10,
            headers={
                "User-Agent": "JobSafe/1.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get("search", []):

            results.append({
                "id": item.get("id"),
                "name": item.get(
                    "label",
                    ""
                ),
                "description": item.get(
                    "description",
                    ""
                )
            })

        return JsonResponse({
            "success": True,
            "results": results
        })

    except requests.RequestException:

        return JsonResponse({
            "success": False,
            "results": [],
            "error": (
                "Company search service is temporarily unavailable."
            )
        })

    except Exception:

        return JsonResponse({
            "success": False,
            "results": [],
            "error": (
                "Something went wrong while searching."
            )
        })


def company_details_api(request):

    company_id = request.GET.get(
        "id",
        ""
    ).strip()

    if not company_id:

        return JsonResponse({
            "success": False,
            "error": "Company ID is required."
        })

    try:

        url = (
            "https://www.wikidata.org/"
            "wiki/Special:EntityData/{}.json"
        )

        response = requests.get(
            url.format(company_id),
            timeout=10,
            headers={
                "User-Agent": "JobSafe/1.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        entity = (
            data
            .get("entities", {})
            .get(company_id, {})
        )

        labels = entity.get(
            "labels",
            {}
        )

        descriptions = entity.get(
            "descriptions",
            {}
        )

        claims = entity.get(
            "claims",
            {}
        )

        def get_claim_value(property_id):

            values = claims.get(
                property_id,
                []
            )

            if not values:
                return ""

            try:

                value = (
                    values[0]
                    ["mainsnak"]
                    ["datavalue"]
                    ["value"]
                )

                if isinstance(
                    value,
                    dict
                ):

                    return value.get(
                        "id",
                        ""
                    )

                return str(value)

            except Exception:

                return ""

        company_name = (
            labels
            .get("en", {})
            .get("value")
            or
            labels
            .get("hi", {})
            .get("value")
            or
            company_id
        )

        description = (
            descriptions
            .get("en", {})
            .get("value")
            or
            descriptions
            .get("hi", {})
            .get("value")
            or
            ""
        )

        website = get_claim_value(
            "P856"
        )

        founded = get_claim_value(
            "P571"
        )

        employees = get_claim_value(
            "P1128"
        )

        ticker = get_claim_value(
            "P414"
        )

        return JsonResponse({

            "success": True,

            "company": {

                "id": company_id,

                "name": company_name,

                "description": description,

                "website": website,

                "founded": founded,

                "employees": employees,

                "ticker": ticker,

                "source": "Wikidata"
            }
        })

    except requests.RequestException:

        return JsonResponse({
            "success": False,
            "error": (
                "Unable to fetch company information."
            )
        })

    except Exception:

        return JsonResponse({
            "success": False,
            "error": (
                "Company details could not be loaded."
            )
        })
        
@user_passes_test(
    lambda u: u.is_staff,
    login_url="/admin-login/"
)
def admin_companies(request):

    companies = (
        CompanyCheck.objects
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "admin-companies.html",
        {
            "companies": companies
        }
    )

@login_required
def scan_history(request):
    jobs = JobCheck.objects.filter(user=request.user).order_by("-created_at")
    companies = CompanyCheck.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "scan-history.html", {"jobs": jobs, "companies": companies, "active": "history"})


@login_required
def risk_analytics(request):
    jobs = JobCheck.objects.filter(user=request.user)
    companies = CompanyCheck.objects.filter(user=request.user)
    context = {
        "total_jobs": jobs.count(),
        "safe_jobs": jobs.filter(risk_level="Safe").count(),
        "suspicious_jobs": jobs.filter(risk_level="Suspicious").count(),
        "high_jobs": jobs.filter(risk_level="High Risk").count(),
        "company_checks": companies.count(),
        "reports": ScamReport.objects.filter(user=request.user).count(),
        "active": "analytics",
    }
    return render(request, "risk-analytics.html", context)


@login_required
def threat_center(request):
    high_jobs = JobCheck.objects.filter(user=request.user, risk_level="High Risk").order_by("-created_at")[:8]
    reports = ScamReport.objects.filter(user=request.user).order_by("-created_at")[:8]
    return render(request, "threat-center.html", {"high_jobs": high_jobs, "reports": reports, "active": "threat"})


@login_required
def alerts(request):
    high = JobCheck.objects.filter(user=request.user, risk_level="High Risk").order_by("-created_at")[:10]
    suspicious = JobCheck.objects.filter(user=request.user, risk_level="Suspicious").order_by("-created_at")[:10]
    return render(request, "alerts.html", {"high": high, "suspicious": suspicious, "active": "alerts"})


@login_required
def resources(request):
    return render(request, "resources.html", {"active": "resources"})


@login_required
def profile(request):
    if request.method == "POST":
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()
        request.user.email = request.POST.get("email", "").strip()
        request.user.save(update_fields=["first_name", "last_name", "email"])
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    return render(request, "profile.html", {"active": "profile"})


@login_required
def security_settings(request):
    if request.method == "POST":
        old = request.POST.get("old_password", "")
        new = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")
        if not request.user.check_password(old):
            messages.error(request, "Current password is incorrect.")
        elif len(new) < 8:
            messages.error(request, "New password must contain at least 8 characters.")
        elif new != confirm:
            messages.error(request, "New passwords do not match.")
        else:
            request.user.set_password(new)
            request.user.save(update_fields=["password"])
            login(request, request.user)
            messages.success(request, "Password changed successfully.")
            return redirect("security_settings")
    return render(request, "security.html", {"active": "security"})


@login_required
def evidence_vault(request):
    reports = ScamReport.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "evidence-vault.html", {"reports": reports, "active": "evidence"})


@user_passes_test(lambda u: u.is_staff, login_url="/admin-login/")
def admin_analytics(request):
    jobs = JobCheck.objects.all()
    context = {
        "users": User.objects.count(),
        "jobs": jobs.count(),
        "high": jobs.filter(risk_level="High Risk").count(),
        "suspicious": jobs.filter(risk_level="Suspicious").count(),
        "safe": jobs.filter(risk_level="Safe").count(),
        "reports": ScamReport.objects.count(),
        "companies": CompanyCheck.objects.count(),
        "active": "admin_analytics",
    }
    return render(request, "admin-analytics.html", context)


@user_passes_test(lambda u: u.is_staff, login_url="/admin-login/")
def admin_intelligence(request):
    jobs = JobCheck.objects.select_related("user").order_by("-created_at")[:15]
    companies = CompanyCheck.objects.select_related("user").order_by("-created_at")[:15]
    return render(request, "admin-intelligence.html", {"jobs": jobs, "companies": companies, "active": "intelligence"})


@user_passes_test(lambda u: u.is_staff, login_url="/admin-login/")
def admin_logs(request):
    return render(request, "admin-logs.html", {"active": "logs"})


@user_passes_test(lambda u: u.is_staff, login_url="/admin-login/")
def admin_system(request):
    return render(request, "admin-system.html", {"active": "system"})

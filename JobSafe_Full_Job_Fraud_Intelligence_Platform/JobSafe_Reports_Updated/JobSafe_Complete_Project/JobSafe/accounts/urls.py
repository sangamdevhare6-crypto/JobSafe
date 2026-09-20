from django.urls import path
from . import views

urlpatterns = [

    path("", views.home, name="home"),

    path("login/", views.login_view, name="login"),

    path("admin-login/", views.admin_login, name="admin_login"),

    path("signup/", views.signup, name="signup"),

    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path("admin-users/", views.admin_users, name="admin_users"),

    path("admin-companies/", views.admin_companies, name="admin_companies"),

    path("safety-guide/", views.safety_guide, name="safety_guide"),

    path("company-check/", views.company_check, name="company_check"),
    path("history/", views.scan_history, name="scan_history"),
    path("risk-analytics/", views.risk_analytics, name="risk_analytics"),
    path("threat-center/", views.threat_center, name="threat_center"),
    path("alerts/", views.alerts, name="alerts"),
    path("resources/", views.resources, name="resources"),
    path("profile/", views.profile, name="profile"),
    path("security/", views.security_settings, name="security_settings"),
    path("evidence-vault/", views.evidence_vault, name="evidence_vault"),
    path("admin-analytics/", views.admin_analytics, name="admin_analytics"),
    path("admin-intelligence/", views.admin_intelligence, name="admin_intelligence"),
    path("admin-logs/", views.admin_logs, name="admin_logs"),
    path("admin-system/", views.admin_system, name="admin_system"),

    path(
        "api/company-search/",
        views.company_search_api,
        name="company_search_api"
    ),

    path(
        "api/company-details/",
        views.company_details_api,
        name="company_details_api"
    ),
]
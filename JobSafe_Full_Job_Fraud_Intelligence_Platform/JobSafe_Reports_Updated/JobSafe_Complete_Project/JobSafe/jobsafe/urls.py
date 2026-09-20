from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("accounts.urls")),
    path("scanner/", include("scanner.urls")),
    path("reports/", include("reports.urls")),
]

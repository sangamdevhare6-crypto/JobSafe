from django.urls import path

from . import views


urlpatterns = [

    path(
        "check-job/",
        views.check_job,
        name="check_job"
    ),

    path(
        "screenshot/",
        views.screenshot_scanner,
        name="screenshot"
    ),

    path(
        "api/analyze-screenshot/",
        views.analyze_screenshot,
        name="analyze_screenshot"
    ),

    path(
        "company/",
        views.company_check,
        name="company_check"
    ),

]
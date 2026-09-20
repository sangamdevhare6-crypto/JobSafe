from django.urls import path
from . import views

urlpatterns = [
    path('', views.scam_reports, name='scam_reports'),
    path('admin/', views.admin_reports, name='admin_reports'),
]

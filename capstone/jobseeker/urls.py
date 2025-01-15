from django.urls import path
from . import views

from .views import *
from django.contrib.auth import views as auth_views

app_name = 'jobseeker'

urlpatterns = [
    path('job_seeker_dashboard/', views.job_seeker_dashboard, name="jobseeker_dashboard"),
    # Jobseeker Profile
    path('job_seeker/profile/', views.job_seeker_profile, name="job_seeker_profile"),

    path('job_seeker/upload_resume/', views.upload_resume, name="upload_resume"),
    path('job_seeker/update_profile/', views.update_profile_bulk, name="update_profile_bulk"),
    # path("update_education/", views.update_education, name="update_education"),
    path('delete-education/<int:id>/', views.delete_education, name='delete-education'),
    path('delete-employment/<int:id>/', views.delete_employment, name='delete-employment'),
    path('job_seeker/delete_profile/', views.delete_profile, name="delete_profile"),

    ]
from django.conf.urls.static import static
from django.urls import path

from capstone import settings
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('companies', views.companies, name="companies"),
    path('employees', views.employees, name="employees"),
    path('jobs', views.jobs, name="jobs"),
    path('accredited_companies', views.accredited_companies, name="accredited_companies"),
    path('seminars', views.seminars, name="seminars"),
    path('profile', views.profile, name="profile"),
    path('job_trends', views.job_trends, name="job_trends"),
    path('tools', views.tools, name="tools"),
    path('faqs', views.faqs, name="faqs"),
    path('analytics', views.analytics, name="analytics"),
    path('job_analytics', views.job_analytics, name="job_analytics"),

    #New urls
    path('job-seeker-dashboard', views.job_seeker_dashboard, name="job_seeker_dashboard"),
    path('employer-dashboard', views.employer_dashboard, name="employer_dashboard"),
    
    # Login and registration paths for PESO staff
    path('register/peso/', views.register_peso, name='register_peso'),
    path('login/peso/', views.login_peso, name='login_peso'),
    path('logout/', views.logout_peso, name="logout_peso"),

    # Login and registration paths for employers
    path('register/employer/', views.register_employer, name='register_employer'),
    path('login/employer/', views.login_employer, name='login_employer'),
    path('logout/', views.logout_employer, name="logout_employer"),
    
    # Login and registration paths for job seekers
    path('register/job-seeker/', views.register_job_seeker, name='register_job_seeker'),
    path('login/job-seeker/', views.login_job_seeker, name='login_job_seeker'),
    path('logout/', views.logout_job_seeker, name="logout_job_seeker"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

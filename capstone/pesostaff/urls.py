
from django.urls import path
from capstone import settings
from . import views
from django.conf.urls.static import static

from .views import jobseeker_location_report, job_location_report, job_vacancy_clustering_report

app_name = 'pesostaff'

urlpatterns = [
    path('', views.staff_dashboard, name='staff_dashboard'),
    path('accreditation/list/', views.requests_view, name='requests_view'),
    path('view_job_postings/', views.view_job_postings, name='view_job_postings'),
    path('accreditation/request/<int:id>/', views.accreditation_request_detail, name='accreditation_request_detail'),
    path('events/', views.get_events, name='get_events'),
    path('events/list/', views.event_list, name='event_list'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/manage/', views.manage_events, name='manage_events'),
    path('update_event/<int:event_id>/', views.update_event, name='update_event'),
    path('delete_event/', views.delete_event, name='delete_event'),
    path('job-location-report/', job_location_report, name='job_location_report'),
    path('jobseeker-location-report/', jobseeker_location_report, name='jobseeker_location_report'),
    path('job-vacancy-report/', job_vacancy_clustering_report, name='job_vacancy_clustering_report'),
    path('jobseeker/list/', views.jobseeker_list, name='jobseeker_list'),
    # path('accreditation/request/<int:id>/', views.accreditation, name='accreditation'),
    # path('accreditation/request/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    # path('accreditation/request/<int:request_id>/reject/', views.reject_request, name='reject_request'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


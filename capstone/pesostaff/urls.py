#
# from capstone import settings
# from . import views
# # from .views import requests
#
# app_name = 'pesostaff'
#
# urlpatterns = [
#     path('', views.staff_dashboard, name='staff_dashboard'),
#     path('accreditation/list/', views.requests_view, name='requests_view'),
#     # path('approve/<int:id>', views.requests, name='requests'),
#     path('view_job_postings/', views.view_job_postings, name='view_job_postings'),
#     path('view_job_posting/<int:id>/', views.view_job_posting, name='view_job_posting'),
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
#
from django.urls import path
from capstone import settings
from . import views
from django.conf.urls.static import static

app_name = 'pesostaff'

urlpatterns = [
    path('', views.staff_dashboard, name='staff_dashboard'),
    path('accreditation/list/', views.requests_view, name='requests_view'),
    path('view_job_postings/', views.view_job_postings, name='view_job_postings'),
    path('accreditation/request/<int:id>/', views.accreditation_request_detail, name='accreditation_request_detail'),
    # path('accreditation/request/<int:id>/', views.accreditation, name='accreditation'),

    # path('accreditation/request/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    # path('accreditation/request/<int:request_id>/reject/', views.reject_request, name='reject_request'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


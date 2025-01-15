from audioop import reverse

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from employer.models import accreditation_document_storage
from jobseeker.models import ResumeDocument, JobseekerProfile, Education, Employment
from .models import CustomUser
from employer.models import AccreditationRequest
from .forms import *

app_name = 'core'

# Create your views here.

def home(request):
    return render(request, f"{app_name}/home.html")

@login_required
def dashboard(request):
    return render(request, f"{app_name}/index.html")

@login_required
def companies(request):
    requests = AccreditationRequest.objects.all()
    return render(request, f"{app_name}/companies.html", {"requests": requests})

@login_required
def accredited_companies(request):
    return render(request, f"{app_name}/accredited-companies.html")

@login_required
def jobs(request):
    return render(request, f"{app_name}/jobs.html")

@login_required
def employees(request):
    return render(request, f"{app_name}/employees.html")

@login_required
def seminars(request):
    return render(request, f"{app_name}/seminars.html")

@login_required
def profile(request):
    return render(request, f"{app_name}/users-profile.html")

@login_required
def job_trends(request):
    return render(request, f"{app_name}/job-trends.html")

@login_required
def tools(request):
    return render(request, f"{app_name}/tools.html")

@login_required
def faqs(request):
    return render(request, f"{app_name}/pages-faq.html")

@login_required
def analytics(request):
    return render(request, f"{app_name}/analytics.html")

@login_required
def job_analytics(request):
    return render(request, f"{app_name}/job-analytics.html")

def employer_dashboard(request):
    return render(request, 'employer/employer_dashboard.html')

def job_seeker_dashboard(request):
    return render(request, 'jobseeker/job_seeker_dashboard.html')

def accreditation_request_list(request):
    accreditation_requests = AccreditationRequest.objects.all()
    return render(request, 'accreditation_request_list.html')

def login_peso(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.user_type == 'PESO':
            login(request, user)
            return redirect('pesostaff:staff_dashboard')  # Replace with the URL you want to redirect to
        else:
            return render(request, 'core/login_peso.html', {'error': 'Invalid credentials or user type.'})
    return render(request, 'core/login_peso.html')  

@login_required
def logout_peso(request):
    logout(request)
    return redirect('home')

def register_peso(request):
    if request.method == 'POST':
        form = PESOStaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login_peso')  # Redirect to login page after registration
    else:
        form = PESOStaffRegistrationForm()
    return render(request, 'core/register_peso.html', {'form': form})


def login_job_seeker(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.user_type == 'JOB_SEEKER':
            login(request, user)
            return redirect('job_seeker_dashboard')  # Replace with the URL you want to redirect to
        else:
            return render(request, 'core/login_job_seeker.html', {'error': 'Invalid credentials or user type.'})
    return render(request, 'core/login_job_seeker.html')

@login_required
def logout_job_seeker(request):
    logout(request)
    return redirect('home')

def register_job_seeker(request):
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # educ_his = EducationHistory.objects.create(user=user)
            # work_his = EmploymentHistory.objects.create(user=user)
            #
            # resume_document = ResumeDocument.objects.create(user=user, educ_his=educ_his, work_his=work_his)
            #
            # JobseekerProfile.objects.create(user=user, resume=resume_document)

            return redirect('login_job_seeker')  # Redirect to login page after registration
    else:
        form = JobSeekerRegistrationForm()
    return render(request, 'core/register_job_seeker.html', {'form': form})

def register_employer(request):
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login_employer')  # Redirect to login page after registration
    else:
        form = EmployerRegistrationForm()
    return render(request, 'core/register_employer.html', {'form': form})

def login_employer(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None and user.user_type == 'EMPLOYER':
            login(request, user)
            return redirect('employer:employer_dashboard')  # Replace with the URL you want to redirect to
        else:
            return render(request, 'core/login_employer.html', {'error': 'Invalid credentials or user type.'})
    return render(request, 'core/login_employer.html')

@login_required
def logout_employer(request):
    logout(request)
    return redirect('home')



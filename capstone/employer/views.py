from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from core.models import CustomUser
from .models import Applicant, JobPosting
from core.forms import *
from .models import *
from .forms import *
from django.urls import reverse
from pesostaff.models import AccreditationRequestApproval


# Create your views here.

def employer_dashboard(request):
    # Query to get all accreditation requests, or specific ones based on your requirement
    accreditation_requests = AccreditationRequest.objects.all()
    return render(request, 'employer/employer_dashboard.html', {'accreditation_requests': accreditation_requests})

# def employer_dashboard(request):
#     return render(request, 'employer/employer_dashboard.html')

@login_required
def logout_employer(request):
    logout(request)
    return redirect('home')

# CompanyProfile view
@login_required
def update_company_profile(request, pk):
    company_profile = get_object_or_404(CompanyProfile, pk=pk)
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=company_profile)
        if form.is_valid():
            form.save()
            # return redirect('company_profile_detail', pk=pk)  # Redirect to detail view or list view
            return redirect(reverse('employer:company_profile_detail', kwargs={'pk': pk}))  # Use reverse with redirect
    else:
        form = CompanyProfileForm(instance=company_profile)
    return render(request, 'employer/update_company_profile.html', {'form': form})

# JobPosting views
@login_required
def create_job_posting(request):
    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            # Get the company profile of the logged-in user
            try:
                employer = CompanyProfile.objects.get(user=request.user)
            except CompanyProfile.DoesNotExist:
                messages.error(request, "You need a company profile to post a job.")
                return redirect('employer:dashboard')

            # Check if accreditation request is approved
            accreditation_request = get_object_or_404(AccreditationRequest, company=employer)
            if accreditation_request.status != 'Approved':
                messages.error(request, "Your accreditation request must be approved before posting a job.")
                return redirect('employer:dashboard')

            # Save the job posting
            job_posting = form.save(commit=False)
            job_posting.company = employer  # Assign the company profile
            job_posting.save()

            messages.success(request, "Job posting created successfully.")
            return redirect('employer:create_job_posting')
    else:
        form = JobPostingForm()

    return render(request, 'employer/create_job_posting.html', {'form': form})

@login_required
def job_posting_list(request):
    job_postings = JobPosting.objects.all()
    return render(request, 'employer/job_posting_list.html', {'job_postings': job_postings})

@login_required
def update_job_posting(request, pk):
    job_posting = get_object_or_404(JobPosting, pk=pk)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job_posting)
        if form.is_valid():
            form.save()
            # return redirect('job_posting_list')
            return redirect(reverse('employer:job_posting_list'))  # Use reverse with redirect
    else:
        form = JobPostingForm(instance=job_posting)
    return render(request, 'employer/update_job_posting.html', {'form': form})

@login_required
def create_accreditation_request(request):
    if request.method == 'POST':
        form = AccreditationRequestForm(request.POST, request.FILES)
        if form.is_valid():
            accreditation_request = form.save()
            return redirect('employer:employer_dashboard')
    else:
        form = AccreditationRequestForm()

    return render(request, 'employer/create_accreditation_request.html', {'form': form})

# @login_required
# def create_accreditation_request(request):
#     if request.method == 'POST':
#         form = AccreditationRequestForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Save the form data
#             accreditation_request = form.save()
#
#             # Perform OCR and validate the document
#             if accreditation_request.document:
#                 # Perform OCR and update document_text
#                 accreditation_request.perform_ocr()
#
#                 # Validate the document based on extracted text
#                 if accreditation_request.validate_document():
#                     accreditation_request.status = 'Pending Review'
#                 else:
#                     accreditation_request.status = 'Rejected'
#
#             else:
#                 # Set the status to 'Rejected' if no document is provided
#                 accreditation_request.status = 'Rejected'
#
#             # Save the updated status
#             accreditation_request.save()
#
#             # Redirect to a success page or dashboard
#             return redirect('employer:employer_dashboard')
#     else:
#         form = AccreditationRequestForm()
#
#     return render(request, 'employer/create_accreditation_request.html', {'form': form})

def load_accreditation_form_fields(request):
    company_type = request.GET.get('company_type')
    form = AccreditationRequestForm(initial={'company_type': company_type})

    return render(request, 'employer/accreditation_form_fields.html', {'form': form})

@login_required
def update_accreditation_request(request, pk):
    accreditation_request = get_object_or_404(AccreditationRequest, pk=pk)
    if request.method == 'POST':
        form = AccreditationRequestForm(request.POST, request.FILES, instance=accreditation_request)
        if form.is_valid():
            form.save()
            # return redirect('accreditation_request_list')
            return redirect(reverse('employer:accreditation_request_list'))
    else:
        form = AccreditationRequestForm(instance=accreditation_request)
    return render(request, 'employer/update_accreditation_request.html', {'form': form})

# Applicant views
@login_required
def update_applicant_resume(request):
    try:
        applicant = Applicant.objects.get(user=request.user)
    except Applicant.DoesNotExist:
        # return redirect('create_applicant')  # Redirect to applicant creation if needed
        return redirect(reverse('employer:create_applicant'))

    if request.method == 'POST':
        form = ApplicantForm(request.POST, request.FILES, instance=applicant)
        if form.is_valid():
            form.save()
            # return redirect('applicant_detail')  # Change to your detail view
            return redirect(reverse('employer:create_applicant'))
    else:
        form = ApplicantForm(instance=applicant)
    return render(request, 'employer/update_applicant_resume.html', {'form': form})

# SavedCandidate views
@login_required
def save_candidate(request, job_id, applicant_id):
    job_posting = get_object_or_404(JobPosting, id=job_id)
    applicant = get_object_or_404(Applicant, id=applicant_id)
    
    SavedCandidate.objects.create(job_posting=job_posting, applicant=applicant)
    # return redirect('saved_candidates_list')  # Change to your list view
    return redirect(reverse('employer:saved_candidates_list'))


# def accreditation_request_overview(request):
#     # Fetch and process the accreditation request data
#     accreditation_requests = AccreditationRequest.objects.all()
#     return render(request, 'employer/accreditation_request_overview.html', {'accreditation_requests': accreditation_requests})

from pesostaff.models import AccreditationRequestApproval


def accreditation_request_overview(request):
    # Get all accreditation requests
    accreditation_requests = AccreditationRequest.objects.all()

    # Loop through accreditation requests and get associated approval comments
    requests_with_approval = []
    for acc_request in accreditation_requests:
        approval = AccreditationRequestApproval.objects.filter(accreditation_request=acc_request).first()
        comments = approval.comments if approval else 'No comments'
        requests_with_approval.append({
            'company': acc_request.company,
            'status': acc_request.get_status_display(),
            'comments': comments
        })

    context = {
        'accreditation_requests': requests_with_approval
    }

    return render(request, 'employer/accreditation_request_overview.html', context)

# def accreditation_request_overview(request):
#     requests = AccreditationRequest.objects.all()
#     # Fetch approval details if they exist
#     approvals = {req.id: AccreditationRequestApproval.objects.filter(accreditation_request=req).first() for req in requests}
#     context = {
#         'requests': requests,
#         'approvals': approvals,
#     }
#     return render(request, 'employer/accreditation_request_overview.html', context)
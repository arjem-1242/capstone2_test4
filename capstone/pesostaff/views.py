from django.contrib.auth.decorators import login_required
from django.db.models.functions import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from employer.models import AccreditationRequest, JobPosting
from pesostaff.models import AccreditationRequestApproval



# @login_required
# def staff_dashboard(request):
#     # Fetch pending accreditation requests and job postings
#     accreditation_requests = AccreditationRequest.objects.filter(status='Pending')
#     job_postings = JobPosting.objects.all()
#
#     context = {
#         'accreditation_requests': accreditation_requests,
#         'job_postings': job_postings,
#     }
#     return render(request, 'pesostaff/staff_dashboard.html', context)
#
#
# # @login_required
# # def approve_accreditation_request(request, id):
# #     # Fetch the specific accreditation request
# #     request_to_approve = get_object_or_404(AccreditationRequest, id=id)
# #
# #     if request.method == 'POST':
# #         form = AccreditationRequestForm(request.POST, request.FILES, instance=request_to_approve)
# #         if form.is_valid():
# #             accreditation_request = form.save(commit=False)
# #             if 'approve' in request.POST:
# #                 accreditation_request.status = 'Approved'
# #             elif 'reject' in request.POST:
# #                 accreditation_request.status = 'Rejected'
# #             accreditation_request.save()
# #             # Redirect to dashboard after approval or rejection
# #             return redirect('pesostaff:staff_dashboard')
# #     else:
# #         form = AccreditationRequestForm(instance=request_to_approve)
# #
# #     context = {
# #         'form': form,
# #         'request': request_to_approve,
# #     }
# #     return render(request, 'pesostaff/approve_accreditation_request.html', context)
# #
# #
# # def some_view(request):
# #     accreditation_requests = AccreditationRequest.objects.all()
# #     return render(request, 'pesostaff/some_template.html', {'accreditation_requests': accreditation_requests})
#
#
# # @login_required
# # def approve_accreditation_request(request, id):
# #     # Fetch the specific accreditation request
# #     request_to_approve = get_object_or_404(AccreditationRequest, id=id)
# #
# #     if request.method == 'POST':
# #         approved = 'approved' in request.POST
# #         comments = request.POST.get('comments', '')
# #
# #         # Create or update the AccreditationRequestApproval instance
# #         approval, created = AccreditationRequestApproval.objects.get_or_create(
# #             accreditation_request=request_to_approve
# #         )
# #         approval.approved = approved
# #         approval.comments = comments
# #         approval.save()
# #
# #         # Update the accreditation request status
# #         request_to_approve.status = 'Approved' if approved else 'Rejected'
# #         request_to_approve.save()
# #
# #         return redirect('pesostaff:staff_dashboard')
# #
# #     context = {
# #         'request': request_to_approve,
# #     }
# #     return render(request, 'pesostaff/approve_accreditation_request.html', context)
#
# @login_required
# def requests_view(request):
#     accreditation_requests = AccreditationRequest.objects.filter(status='Pending')
#
#     context = {
#         'accreditation_requests': accreditation_requests,
#     }
#     return render(request, 'pesostaff/approve_accreditation_request.html', context)
#
# # @login_required
# # def requests(request, id):
# #     if id:
# #         # Fetch the specific accreditation request
# #         request_to_approve = get_object_or_404(AccreditationRequest, id=id)
# #
# #         if request.method == 'POST':
# #             # Handle approval or rejection
# #             if 'approve' in request.POST:
# #                 approved = True
# #             elif 'reject' in request.POST:
# #                 approved = False
# #
# #             comments = request.POST.get('comments', '')
# #
# #             # Create or update the AccreditationRequestApproval instance
# #             approval, created = AccreditationRequestApproval.objects.get_or_create(
# #                 accreditation_request=request_to_approve
# #             )
# #             approval.approved = approved
# #             approval.comments = comments
# #             approval.save()
# #
# #             # Update the accreditation request status
# #             request_to_approve.status = 'Approved' if approved else 'Rejected'
# #             request_to_approve.save()
# #
# #             return redirect('pesostaff:staff_dashboard')
# #
# #         context = {
# #             'request': request_to_approve,
# #         }
# #         return render(request, 'pesostaff/approve_accreditation_request.html', context)
# #     else:
# #         # If no specific ID, show a list of requests
# #         accreditation_requests = AccreditationRequest.objects.all()
# #         context = {
# #             'accreditation_requests': accreditation_requests,
# #         }
# #         return render(request, 'pesostaff/approve_accreditation_request.html', context)
#
#
# @login_required
# def accreditation_request_detail(request, request_id):
#     accreditation_request = get_object_or_404(AccreditationRequest, id=request_id)
#     return render(request, 'pesostaff/accreditation_request_detail.html', {'accreditation_request': accreditation_request})
#
#
# @login_required
# def view_job_postings(request):
#     # Fetch all job postings
#     job_postings = JobPosting.objects.all()
#
#     context = {
#         'job_postings': job_postings,
#     }
#     return render(request, 'pesostaff/view_job_postings.html', context)
#
#
# @login_required
# def view_job_posting(request, id):
#     # Fetch the specific job posting
#     job_posting = get_object_or_404(JobPosting, id=id)
#
#     context = {
#         'job_posting': job_posting,
#     }
#     return render(request, 'pesostaff/view_job_postings.html', context)
#
# @login_required
# def logout_view(request):
#     logout(request)
#     return redirect('core/index.html')  # Redirect to the login page or another page after logout

def staff_dashboard(request):
    pending_requests_count = AccreditationRequest.objects.filter(status='Pending').count()

    # Count all job postings
    all_job_postings_count = JobPosting.objects.count()

    context = {
        'pending_requests_count': pending_requests_count,
        'all_job_postings_count': all_job_postings_count,
    }
    return render(request, 'pesostaff/staff_dashboard.html', context)

def requests_view(request):
    requests = AccreditationRequest.objects.all()
    return render(request, 'pesostaff/request_view.html', {'requests': requests})

def view_job_postings(request):
    job_postings = JobPosting.objects.all()  # Assume JobList is your model for job postings
    return render(request, 'pesostaff/view_job_postings.html', {'job_postings': job_postings})

# def accreditation_request_detail(request, id):
#     # Retrieve the AccreditationRequest
#     accreditation_request = get_object_or_404(AccreditationRequest, id=id)
#
#     # Try to get the related AccreditationRequestApproval
#     approval = AccreditationRequestApproval.objects.filter(accreditation_request=accreditation_request).first()
#
#     if request.method == 'POST':
#         # Check if the request is to approve or reject the request
#         if 'approve' in request.POST:
#             if approval is None:
#                 # Create a new approval record
#                 approval = AccreditationRequestApproval(accreditation_request=accreditation_request, approved=True)
#             else:
#                 # Update existing approval record
#                 approval.approved = True
#             approval.comments = request.POST.get('comments', '')
#             approval.save()
#
#         elif 'reject' in request.POST:
#             if approval is None:
#                 # Create a new rejection record
#                 approval = AccreditationRequestApproval(accreditation_request=accreditation_request, approved=False)
#             else:
#                 # Update existing approval record
#                 approval.approved = False
#             approval.comments = request.POST.get('comments', '')
#             approval.save()
#
#         # Redirect to the same request detail page after action
#         return redirect('pesostaff:accreditation_request_detail', id=id)
#
#
#
#     # Retrieve related documents
#     related_documents = accreditation_request.get_documents()
#
#     # Prepare context with the accreditation request, approval details, and related documents
#     context = {
#         'request': accreditation_request,
#         'approval': approval,
#         'documents': related_documents,
#     }
#
#     # Render the detail template with the context
#     return render(request, 'pesostaff/accreditation_request_detail.html', context)


# def accreditation_request_detail(request, id):
#     # Retrieve the AccreditationRequest
#     accreditation_request = get_object_or_404(AccreditationRequest, id=id)
#
#     # Try to get the related AccreditationRequestApproval
#     approval = AccreditationRequestApproval.objects.filter(accreditation_request=accreditation_request).first()
#
#     if request.method == 'POST':
#         # Check if the request is to approve or reject the request
#         if 'approve' in request.POST:
#             if approval is None:
#                 # Create a new approval record
#                 approval = AccreditationRequestApproval(accreditation_request=accreditation_request, approved=True)
#             else:
#                 # Update existing approval record
#                 approval.approved = True
#             approval.comments = request.POST.get('comments', '')
#             approval.save()
#
#         elif 'reject' in request.POST:
#             if approval is None:
#                 # Create a new rejection record
#                 approval = AccreditationRequestApproval(accreditation_request=accreditation_request, approved=False)
#             else:
#                 # Update existing approval record
#                 approval.approved = False
#             approval.comments = request.POST.get('comments', '')
#             approval.save()
#
#         # Redirect to the same request detail page after action
#         return redirect('pesostaff:accreditation_request_detail', id=id)
#
#     # Retrieve related documents
#     related_documents = accreditation_request.get_documents()
#
#     # Prepare context with the accreditation request, approval details, and related documents
#     context = {
#         'request': accreditation_request,
#         'approval': approval,
#         'documents': related_documents
#     }
#
#     # Render the detail template with the context
#     return render(request, 'pesostaff/accreditation_request_detail.html', context)

# @login_required
# def accreditation(request, id):
#     if id:
#         # Fetch the specific accreditation request
#         request_to_approve = get_object_or_404(AccreditationRequest, id=id)
#
#         if request.method == 'POST':
#             # Initialize approved variable
#             approved = None
#
#             # Handle approval or rejection
#             if 'approve' in request.POST:
#                 approved = True
#             elif 'reject' in request.POST:
#                 approved = False
#
#             comments = request.POST.get('comments', '')
#
#             if approved is not None:
#                 # Create or update the AccreditationRequestApproval instance
#                 approval, created = AccreditationRequestApproval.objects.get_or_create(
#                     accreditation_request=request_to_approve
#                 )
#                 approval.approved = approved
#                 approval.comments = comments
#                 approval.save()
#
#                 # Update the accreditation request status
#                 request_to_approve.status = 'Approved' if approved else 'Rejected'
#                 request_to_approve.save()
#
#                 return redirect('pesostaff:staff_dashboard')
#
#         context = {
#             'request': request_to_approve,
#         }
#         return render(request, 'pesostaff:accreditation_request_detail.html', context)
#     else:
#         # If no specific ID, show a list of requests
#         accreditation_requests = AccreditationRequest.objects.all()
#         context = {
#             'accreditation_requests': accreditation_requests,
#         }
#         return render(request, 'pesostaff:accreditation_request_detail.html', context)
#

#
# def accreditation_request_detail(request, id):
#     accreditation_request = get_object_or_404(AccreditationRequest, id=id)
#     approval = AccreditationRequestApproval.objects.filter(accreditation_request=accreditation_request).first()
#
#     if request.method == 'POST':
#         if 'approve' in request.POST:
#             if approval is None:
#                 approval = AccreditationRequestApproval(accreditation_request=accreditation_request, approved=True)
#             else:
#                 approval.approved = True
#             approval.comments = request.POST.get('comments', '')
#             approval.save()
#
#             accreditation_request.status = 'Approved'
#             accreditation_request.save()
#
#         elif 'reject' in request.POST:
#             if approval is None:
#                 approval = AccreditationRequestApproval(accreditation_request=accreditation_request, approved=False)
#             else:
#                 approval.approved = False
#             approval.comments = request.POST.get('comments', '')
#             approval.save()
#
#             accreditation_request.status = 'Rejected'
#             accreditation_request.save()
#
#         return redirect('pesostaff:accreditation_request_detail', id=id)
#
#     related_documents = accreditation_request.get_documents()
#
#     context = {
#         'request': accreditation_request,
#         'approval': approval,
#         'documents': related_documents
#     }
#
#     return render(request, 'pesostaff/accreditation_request_detail.html', context)

def accreditation_request_detail(request, id):
    accreditation_request = get_object_or_404(AccreditationRequest, id=id)
    approval, created = AccreditationRequestApproval.objects.get_or_create(accreditation_request=accreditation_request)

    if request.method == 'POST':
        if 'approve' in request.POST:
            approval.approved = True
            accreditation_request.status = 'Approved'
        elif 'reject' in request.POST:
            approval.approved = False
            accreditation_request.status = 'Rejected'

        approval.comments = request.POST.get('comments', '')
        approval.save()
        accreditation_request.save()

        return redirect('pesostaff:accreditation_request_detail', id=id)

    related_documents = accreditation_request.get_documents()

    context = {
        'request': accreditation_request,
        'approval': approval,
        'documents': related_documents
    }

    return render(request, 'pesostaff/accreditation_request_detail.html', context)

# def approve_request(request, id):
#     accreditation_request = get_object_or_404(AccreditationRequest, id=id)
#     comments = request.POST.get('comments', '')
#
#     approval, created = AccreditationRequestApproval.objects.get_or_create(
#         accreditation_request=accreditation_request
#     )
#     approval.approved = True
#     approval.comments = comments
#     approval.save()
#
#     accreditation_request.status = 'Approved'
#     accreditation_request.save()
#
# def reject_request(request, id):
#     accreditation_request = get_object_or_404(AccreditationRequest, id=id)
#     comments = request.POST.get('comments', '')
#
#     approval, created = AccreditationRequestApproval.objects.get_or_create(
#         accreditation_request=accreditation_request
#     )
#     approval.approved = False
#     approval.comments = comments
#     approval.save()
#
#     accreditation_request.status = 'Rejected'
#     accreditation_request.save()
#

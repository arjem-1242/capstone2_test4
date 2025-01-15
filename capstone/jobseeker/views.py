from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .utils import extract_text_from_resume, parse_resume_text, update_user_resume, handle_new_entry
from .forms import *
from datetime import datetime
import logging
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from jobseeker.models import ResumeDocument, Education, Employment


logger = logging.getLogger(__name__)
# Create your views here.

def job_seeker_dashboard(request):
    return render(request, 'jobseeker/job_seeker_dashboard.html')


@login_required
def logout_job_seeker(request):
    logout(request)
    return redirect('home')


@login_required
def job_seeker_profile(request):
    profile = get_object_or_404(JobseekerProfile, user=request.user)
    resume = profile.resume  # Assuming `JobseekerProfile` has a `resume` relation.

    # Query related education and employment entries
    education_set = profile.resume.education_entries.all() if resume else []
    employment_set = profile.resume.employment_entries.all() if resume else []

    if request.method == 'POST':
        form = JobseekerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('jobseeker:job_seeker_profile')  # Redirect to the profile view after saving
    else:
        form = JobseekerProfileForm(instance=profile)

    # Include education and employment data in the context
    return render(
        request,
        'jobseeker/job_seeker_profile.html',
        {
            'profile': profile,
            'form': form,
            'education_set': education_set,
            'employment_set': employment_set,
        }
    )

@login_required
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if there's already a ResumeDocument for the user
            resume_doc, created = ResumeDocument.objects.get_or_create(user=request.user)

            # If an existing resume file is present, delete it to replace with the new one
            if not created:
                resume_doc.resume.delete(save=False)

            # Update the resume file with the new uploaded file
            resume_doc.resume = form.cleaned_data['resume']
            resume_doc.save()

            # Perform extraction and parsing as before
            file_path = resume_doc.resume.path
            resume_text = extract_text_from_resume(file_path)
            parsed_data = parse_resume_text(resume_text)

            # Save extracted and parsed data to the ResumeDocument
            resume_doc.raw_text = resume_text
            resume_doc.parsed_data = parsed_data
            resume_doc.processed = True
            resume_doc.status = "Completed"  # Mark as completed
            resume_doc.save()

            # Temporarily store parsed data in the session
            request.session['temp_parsed_data'] = parsed_data

            # # Update user profile with parsed data
            update_user_resume(request.user, parsed_data)

            # return redirect('jobseeker:update_profile')  # Redirect to the update profile page
            return redirect('jobseeker:job_seeker_profile')  # Redirect to the user's profile page or success page
    else:
        form = ResumeUploadForm()
    return render(request, 'jobseeker/upload_resume.html', {'form': form})
#
# @csrf_exempt
# def update_profile(request):
#     if request.method == "POST":
#         field = request.POST.get("field")
#         value = request.POST.get("value")
#         user = request.user
#         resume = ResumeDocument.objects.get(user=user)
#
#         if field in ["phone", "skills"]:
#             setattr(resume, field, value)
#             resume.save()
#             return JsonResponse({"success": True, "message": f"{field} updated successfully!"})
#
#         return JsonResponse({"success": False, "message": "Invalid field!"})
#     return JsonResponse({"success": False, "message": "Invalid request!"})

# def update_profile_bulk(request):
#     if request.method == "POST":
#         changes = json.loads(request.POST.get("changes", "[]"))
#
#         # Get the resume object
#         resume = ResumeDocument.objects.get(user=request.user)
#
#         for change in changes:
#             field = change.get("field")
#             value = change.get("value")
#             record_id = change.get("id")
#
#             if record_id:
#                 # Update specific Education or Employment records
#                 if field in ["school", "degree", "started", "finished"]:
#                     Education.objects.filter(id=record_id).update(**{field: value})
#                 elif field in ["company", "position", "hired", "resigned"]:
#                     Employment.objects.filter(id=record_id).update(**{field: value})
#             else:
#                 # Handle new entries for Education or Employment
#                 if field in ["school", "program", "started", "finished", "company", "role", "hired", "resigned"]:
#                     handle_new_entry(change, resume, request.user)
#                 else:
#                     # Update global fields (e.g., resume phone, skills)
#                     setattr(resume, field, value)
#                     resume.save()
#
#         return JsonResponse({"success": True})
#
#     return JsonResponse({"error": "Invalid request method."}, status=400)

def update_profile_bulk(request):
    if request.method == "POST":
        changes = request.POST.get("changes")
        if not changes:
            return JsonResponse({"error": "No changes provided"}, status=400)

        try:
            changes = json.loads(changes)
            for change in changes:
                field = change.get("field")
                record_id = change.get("id")
                value = change.get("value")

                # Determine the model and field
                if field in ["school", "program", "started", "finished"]:
                    record = Education.objects.get(id=record_id)
                elif field in ["company", "role", "hired", "resigned"]:
                    record = Employment.objects.get(id=record_id)
                else:
                    return JsonResponse({"error": "Invalid field"}, status=400)

                # Handle date fields
                if field in ["started", "finished", "hired", "resigned"]:
                    try:
                        # Parse date in expected format
                        value = datetime.strptime(value, "%Y-%m-%d").date()
                    except ValueError:
                        return JsonResponse({"error": f"Invalid date format for {field}. Use YYYY-MM-DD."}, status=400)

                # Update the field
                if hasattr(record, field):
                    setattr(record, field, value)
                    record.save()
                else:
                    return JsonResponse({"error": f"Field '{field}' does not exist."}, status=400)

            return JsonResponse({"success": "All changes updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

# @csrf_exempt
# def update_education(request):
#     if request.method == "POST":
#         field = request.POST.get("field")
#         value = request.POST.get("value")
#         education_id = request.POST.get("id")
#         try:
#             education = Education.objects.get(id=education_id)
#             setattr(education, field, value)
#             education.save()
#             return JsonResponse({"success": True, "message": f"Education {field} updated successfully!"})
#         except Education.DoesNotExist:
#             return JsonResponse({"success": False, "message": "Education record not found!"})

# @csrf_exempt
# def update_employment(request):
#     if request.method == "POST":
#         field = request.POST.get("field")
#         value = request.POST.get("value")
#         employment_id = request.POST.get("id")
#         try:
#             employment = Employment.objects.get(id=employment_id)
#             setattr(employment, field, value)
#             employment.save()
#             return JsonResponse({"success": True, "message": f"Employment {field} updated successfully!"})
#         except Employment.DoesNotExist:
#             return JsonResponse({"success": False, "message": "Employment record not found!"})
#
# @login_required
# def update_profile(request): # Retrieve temporarily parsed data
#     temp_data = request.session.get('temp_parsed_data', {})
#
#     if request.method == 'POST':
#         # Process form submission to update the profile
#         profile_form = JobseekerProfileForm(request.POST, instance=request.user)
#         if profile_form.is_valid():
#             # Update the user's main profile details
#             profile_form.save()
#
#             # Update related models (Education and Employment)
#             update_related_models(request.user, temp_data)
#
#             # Clear temporary data after saving
#             request.session.pop('temp_parsed_data', None)
#
#             messages.success(request, "Profile updated successfully!")
#             return redirect('jobseeker:job_seeker_profile')  # Redirect to the profile page
#
#     else:
#         # Pre-fill form with parsed data
#         profile_form = JobseekerProfileForm(instance=request.user)
#
#     return render(request, 'jobseeker/update_profile.html', {
#         'form': profile_form,
#         'temp_data': temp_data,
#     })


@csrf_exempt
def delete_education(request, id):
    if request.method == "POST":
        try:
            education = Education.objects.get(id=id)
            education.delete()
            return JsonResponse({"success": True})
        except Education.DoesNotExist:
            return JsonResponse({"success": False, "error": "Education not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@csrf_exempt
def delete_employment(request, id):
    if request.method == "POST":
        try:
            employment = Employment.objects.get(id=id)
            employment.delete()
            return JsonResponse({"success": True})
        except Education.DoesNotExist:
            return JsonResponse({"success": False, "error": "Employment not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})

@login_required
def delete_profile(request):
    if request.method == "POST":
        confirmation = request.POST.get("delete_confirmation")
        if confirmation == "yes":
            user = request.user
            user.delete()  # Deletes the user account
            logout(request)  # Log out the user
            messages.success(request, "Your account has been deleted successfully.")
            return redirect("home")  # Redirect to home or any other page
        else:
            messages.info(request, "Account deletion canceled.")
            return redirect('jobseeker:job_seeker_profile')  # Redirect back to profile or dashboard

    return render(request, 'jobseeker/delete_profile.html')
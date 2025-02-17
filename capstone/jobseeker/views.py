from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from employer.models import JobPosting
from employer.views import job_posting_list
from .utils import extract_text_from_resume, parse_resume_text, update_user_resume, handle_new_entry
from .forms import *
from datetime import datetime
import logging
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from jobseeker.models import ResumeDocument, Education, Employment
from .job_matching import match_resume_to_jobs
from .models import *
from employer.models import *
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *


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
            # Temporarily store parsed data in the session
            request.session['temp_parsed_data'] = parsed_data
            print("Parsed Data Stored in Session:", request.session['temp_parsed_data'])

            # # Update user profile with parsed data
            update_user_resume(request.user, parsed_data)

            # return redirect('jobseeker:update_profile')  # Redirect to the update profile page
            return redirect('jobseeker:job_seeker_profile')  # Redirect to the user's profile page or success page
    else:
        form = ResumeUploadForm()
    return render(request, 'jobseeker/upload_resume.html', {'form': form})

@csrf_exempt
def update_profile_field(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            field = data.get("field")
            value = data.get("value")

            # Get the user's resume profile (Adjust based on your authentication setup)
            profile = JobseekerProfile.objects.get(user=request.user)
            resume = profile.resume # Assuming one-to-one relationship

            # Update only if the field exists in ResumeDocument
            if hasattr(resume, field):
                setattr(resume, field, value)
                resume.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Invalid field"}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

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


def view_matched_jobs(request):
    try:
        logger.info("Attempting to retrieve ResumeDocument for user: %s", request.user)

        # Ensure you're retrieving the correct resume document
        resume_document = ResumeDocument.objects.get(user=request.user)
        educ_his = Education.objects.filter(user=request.user)
        work_his = Employment.objects.filter(user=request.user)
        logger.info("ResumeDocument retrieved successfully for user: %s", request.user)

        # Prepare resume data for matching
        resume_data = {

            'skills': resume_document.skills.split(','),  # Assuming skills are stored as a comma-separated string
            'location': resume_document.location,
            'requirements': [edu.program for edu in educ_his],  # List of programs
            'position': [work.role for work in work_his],  # List of roles

        }
        logger.debug("Prepared resume data for matching: %s", resume_data)

        # Retrieve all job postings
        job_postings = JobPosting.objects.all()
        logger.info("Retrieved all job postings. Count: %d", job_postings.count())

        # Match resume to jobs using jobmatching.py
        matched_jobs = match_resume_to_jobs(resume_data, job_postings)
        logger.info("Matched jobs retrieved for user %s. Count: %d", request.user, len(matched_jobs))

        # Loop through each job posting and process
        for job in matched_jobs:
            # Ensure job has an 'id' field and access it correctly
            job_posting = next((job_posting for job_posting in job_postings if job_posting.id == job.get('id')), None)

            if job_posting:
                job_posting_id = job_posting.id  # ✅ Access the job posting ID

                job_skills = job.get('skills', '').split(',') if job.get('skills') else []
                matched_skills = list(set(resume_data.get('skills', [])) & set(job_skills))

                matched_location = job.get('location', '') if resume_data.get('location', '') == job.get('location',
                                                                                                         '') else ""

                job_requirements = job.get('requirements', '').split(',') if job.get('requirements') else []
                matched_education = list(set(resume_data.get('requirements', [])) & set(job_requirements))

                matched_position = job.get('position', '')

                # Create or get matched job record
                matched_job, created = MatchedJobs.objects.get_or_create(
                    user=request.user,
                    resume_id=resume_document.id,  # ✅ Correct resume ID
                    job_posting_id=job_posting_id,  # ✅ Correct job posting ID
                    defaults={
                        'matched_on': timezone.now(),
                        'matched_skills': ','.join(matched_skills),
                        'matched_location': matched_location,
                        'matched_position': matched_position,
                        'matched_education': ','.join(matched_education),
                    }
                )

                if created:
                    logger.info("Saved matched job: %s for user: %s", matched_position, request.user)
            else:
                logger.error("Skipping job due to missing or invalid job posting ID: %s", job)

        return render(request, 'jobseeker/matched_jobs.html', {'matched_jobs': matched_jobs})
    except ResumeDocument.DoesNotExist:
        logger.error("ResumeDocument does not exist for user: %s", request.user)
        return render(request, 'jobseeker/job_seeker_dashboard.html', {'error': 'Resume document not found'})
    except Exception as e:
        logger.exception("An error occurred while fetching matched jobs for user: %s", request.user)
        return render(request, 'jobseeker/job_seeker_dashboard.html', {'error': 'An unexpected error occurred'})


@csrf_exempt
@login_required
def add_education(request):
    if request.method == "POST":
        user = request.user

        # Try to fetch the resume linked to the user
        try:
            resume = ResumeDocument.objects.get(user=user)
        except ResumeDocument.DoesNotExist:
            return JsonResponse({"error": "Resume not found for the user"}, status=404)

        # Create a blank education entry linked to the resume
        education = Education.objects.create(
            user=user, school="", program="", started=None, finished=None, resume=resume
        )

        return JsonResponse({
            "message": "New education record created",
            "id": education.id,
            "school": education.school,
            "program": education.program,
            "started": None,
            "finished": None,
            "resume": resume.id  # Include resume ID in response
        })

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
@login_required
def update_education(request, education_id):
    if request.method == "POST":
        user = request.user
        try:
            education = Education.objects.get(id=education_id, user=user)
            field = request.POST.get("field")
            value = request.POST.get("value")

            if field and value is not None:
                setattr(education, field, value)  # Dynamically update the field
                education.save()
                return JsonResponse({"message": f"{field} updated successfully", "value": value})

            return JsonResponse({"error": "Invalid field or value"}, status=400)

        except Education.DoesNotExist:
            return JsonResponse({"error": "Education entry not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)




@csrf_exempt
@login_required
def delete_education(request, education_id):
    if request.method == "POST":
        try:
            education = Education.objects.get(id=education_id, user=request.user)
            education.delete()
            return JsonResponse({"message": "Education entry deleted successfully"})
        except Education.DoesNotExist:
            return JsonResponse({"error": "Education entry not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)



@csrf_exempt
@login_required
def add_employment(request):
    if request.method == "POST":
        user = request.user

        # Try to fetch the resume linked to the user
        try:
            resume = ResumeDocument.objects.get(user=user)
        except ResumeDocument.DoesNotExist:
            return JsonResponse({"error": "Resume not found for the user"}, status=404)

        # Create a blank employment entry linked to the resume
        employment = Employment.objects.create(
            user=user, company="", role="", hired=None, resigned=None, resume=resume
        )

        return JsonResponse({
            "message": "New employment record created",
            "id": employment.id,
            "company": employment.company,
            "position": employment.role,
            "hired": None,
            "resigned": None,
            "resume": resume.id  # Include resume ID in response
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@login_required
def update_employment(request, employment_id):
    if request.method == "POST":
        user = request.user
        try:
            employment = Employment.objects.get(id=employment_id, user=user)
            field = request.POST.get("field")
            value = request.POST.get("value")

            if field and value is not None:
                setattr(employment, field, value)  # Dynamically update the field
                employment.save()
                return JsonResponse({"message": f"{field} updated successfully", "value": value})

            return JsonResponse({"error": "Invalid field or value"}, status=400)

        except Employment.DoesNotExist:
            return JsonResponse({"error": "Employment entry not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
@login_required
def delete_employment(request, employment_id):
    if request.method == "POST":
        try:
            employment = Employment.objects.get(id=employment_id, user=request.user)
            employment.delete()
            return JsonResponse({"message": "Employment entry deleted successfully"})
        except Employment.DoesNotExist:
            return JsonResponse({"error": "Employment entry not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)


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
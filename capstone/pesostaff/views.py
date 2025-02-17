from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from employer.models import AccreditationRequest, JobPosting, CompanyProfile
from jobseeker.models import ResumeDocument, JobseekerProfile
from pesostaff.models import AccreditationRequestApproval
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Event
from .forms import EventForm
import logging

logger = logging.getLogger(__name__)
@login_required
def staff_dashboard(request):
    # Job Locations
    location_data = (
        JobPosting.objects.values('location')
        .annotate(count=Count('id'))
        .order_by('-count')  # Sort by most frequent locations
    )

    #Job Seeker Locations
    location_job_data = ResumeDocument.objects.values('location').exclude(location='').annotate(count=Count('location'))

    # Job Vacancies

    job_data = JobPosting.objects.values('position', 'date_posted', 'no_of_vacancies')

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(job_data))

    # If there are fewer than 2 job postings, skip clustering
    if len(df) < 2:
        return render(request, 'pesostaff/job_vacancy_clustering_report.html', {
            'graph_json': None,  # No clustering possible
            'clustered_data': df.to_dict(orient='records')  # Return data as is
        })

    # Handle missing values
    df['no_of_vacancies'] = pd.to_numeric(df['no_of_vacancies'], errors='coerce').fillna(0).astype(int)
    df['date_posted'] = df['date_posted'].astype(str)

    # Apply K-Modes clustering
    num_clusters = min(3, len(df))  # Ensure clusters do not exceed data points
    km = KModes(n_clusters=num_clusters, init='Huang', n_init=5, verbose=1)

    clusters = km.fit_predict(df[['position', 'date_posted', 'no_of_vacancies']].astype(str))

    # Add cluster labels to DataFrame
    df['Cluster'] = clusters

    # Create an interactive line chart using Plotly
    fig = go.Figure()

    for cluster in sorted(df['Cluster'].unique()):
        cluster_data = df[df['Cluster'] == cluster].groupby('date_posted')['no_of_vacancies'].sum()
        fig.add_trace(
            go.Scatter(
                x=cluster_data.index,
                y=cluster_data.values,
                mode='lines+markers',
                name=f'Cluster {cluster}'
            )
        )

    # Update layout for better aesthetics
    fig.update_layout(
        title='Job Vacancies Clustering Report',
        xaxis_title='Date Posted',
        yaxis_title='Number of Vacancies',
        legend_title='Clusters',
        template='plotly_white',
    )

    # Convert the Plotly figure to JSON for embedding in the template
    graph_json = fig.to_json()

    # Count objects
    all_job_postings_count = JobPosting.objects.count()
    all_job_seeker_count = JobseekerProfile.objects.count()
    all_accreditation_request = AccreditationRequest.objects.count()

    context = {
        'all_job_postings_count': all_job_postings_count,
        'all_job_seeker_count': all_job_seeker_count,
        'all_accreditation_request': all_accreditation_request,
        'graph_json': graph_json,
        'clustered_data': df.to_dict(orient='records'),
        'location_data': location_data,
        'location_job_data': location_job_data,
    }
    return render(request, 'pesostaff/staff_dashboard.html', context)

def requests_view(request):
    requests = AccreditationRequest.objects.all()
    return render(request, 'pesostaff/request_view.html', {'requests': requests})

def view_job_postings(request):
    try:
        job_postings = JobPosting.objects.all()
        # Debugging: Print job postings to console (remove in production)
        for job in job_postings:
            print(f"Position: {job.position}, Employer: {job.company.user.company_name}")
    except Exception as e:
        print(f"Error fetching job postings: {e}")
        job_postings = []

    return render(request, 'pesostaff/view_job_postings.html', {'job_postings': job_postings})

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


@require_POST
def add_event(request):
    if request.method == 'POST':
        print("Received POST data:", request.POST)  # Debugging line

        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)

            # Debugging: Print extracted values
            print("Extracted start_date:", event.start_date)
            print("Extracted end_date:", event.end_date)

            if not event.start_date or not event.end_date:
                return JsonResponse({'error': 'Start date and End date are required.'}, status=400)

            event.save()

            return JsonResponse({
                'id': event.id,
                'title': event.title,
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
            })
        else:
            print("Form errors:", form.errors)  # Debugging form errors
            return JsonResponse({'error': 'Invalid form submission.', 'errors': form.errors}, status=400)


def update_event(request, event_id):
    """Handles event updating."""
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Event updated successfully'})
        return JsonResponse({'errors': form.errors}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)


@require_POST
def delete_event(request):
    """Handles event deletion via AJAX."""
    if request.user.is_staff:
        event_id = request.POST.get('event_id')
        event = get_object_or_404(Event, pk=event_id)
        event.delete()
        return JsonResponse({'message': 'Event deleted successfully!'})

    return JsonResponse({'error': 'Unauthorized'}, status=403)


def get_events(request):
    """Fetches all events for display."""
    events = Event.objects.all()
    event_data = [
        {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'location': event.location,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
        }
        for event in events
    ]
    return JsonResponse(event_data, safe=False)


def manage_events(request):
    """Handles event management for staff users."""
    if not request.user.is_staff:
        return redirect('home')

    message = None
    form = EventForm()

    if request.method == 'POST':
        if 'add_event' in request.POST:
            form = EventForm(request.POST)
            if form.is_valid():
                form.save()
                message = "Event added successfully!"
                form = EventForm()  # Reset form

        elif 'update_event' in request.POST:
            event = get_object_or_404(Event, pk=request.POST.get('event_id'))
            form = EventForm(request.POST, instance=event)
            if form.is_valid():
                form.save()
                message = "Event updated successfully!"

        elif 'delete_event' in request.POST:
            event = get_object_or_404(Event, pk=request.POST.get('event_id'))
            event.delete()
            message = "Event deleted successfully!"

    events = Event.objects.all()
    return render(request, 'pesostaff/manage_events.html', {'form': form, 'events': events, 'message': message})


def event_list(request):
    events = Event.objects.all()
    event_data = []
    for event in events:
        event_info = {
            'title': event.title,
            'description': event.description,
            'location': event.location,
            'id': event.id,
        }

        # Ensure start_time and end_time are not None before calling isoformat()
        if event.start_date:
            event_info['start'] = event.start_date.isoformat()
        else:
            event_info['start'] = None

        if event.end_date:
            event_info['end'] = event.end_date.isoformat()
        else:
            event_info['end'] = None

        event_data.append(event_info)

    return JsonResponse(event_data, safe=False)


def job_location_report(request):
    # Get job postings grouped by location
    location_data = (
        JobPosting.objects.values('location')
        .annotate(count=Count('id'))
        .order_by('-count')  # Sort by most frequent locations
    )

    context = {
        'location_data': location_data
    }

    return render(request, 'pesostaff/job_location_report.html', context)


def jobseeker_location_report(request):
    # Querying job seekers by location
    location_job_data = ResumeDocument.objects.values('location').exclude(location='').annotate(count=Count('location'))

    return render(request, 'pesostaff/jobseeker_location_report.html', {'location_job_data': location_job_data})



from employer.models import JobPosting
import pandas as pd
from kmodes.kmodes import KModes
import plotly.graph_objects as go
from django.shortcuts import render

def job_vacancy_clustering_report(request):
    # Retrieve job posting data
    job_data = JobPosting.objects.values('position', 'date_posted', 'no_of_vacancies')

    # Convert QuerySet to DataFrame
    df = pd.DataFrame(list(job_data))

    # If there are fewer than 2 job postings, skip clustering
    if len(df) < 2:
        return render(request, 'pesostaff/job_vacancy_clustering_report.html', {
            'graph_json': None,  # No clustering possible
            'clustered_data': df.to_dict(orient='records')  # Return data as is
        })

    # Handle missing values
    df['no_of_vacancies'] = pd.to_numeric(df['no_of_vacancies'], errors='coerce').fillna(0).astype(int)
    df['date_posted'] = df['date_posted'].astype(str)

    # Apply K-Modes clustering
    num_clusters = min(3, len(df))  # Ensure clusters do not exceed data points
    km = KModes(n_clusters=num_clusters, init='Huang', n_init=5, verbose=1)

    clusters = km.fit_predict(df[['position', 'date_posted', 'no_of_vacancies']].astype(str))

    # Add cluster labels to DataFrame
    df['Cluster'] = clusters

    # Create an interactive line chart using Plotly
    fig = go.Figure()

    for cluster in sorted(df['Cluster'].unique()):
        cluster_data = df[df['Cluster'] == cluster].groupby('date_posted')['no_of_vacancies'].sum()
        fig.add_trace(
            go.Scatter(
                x=cluster_data.index,
                y=cluster_data.values,
                mode='lines+markers',
                name=f'Cluster {cluster}'
            )
        )

    # Update layout for better aesthetics
    fig.update_layout(
        title='Job Vacancies Clustering Report',
        xaxis_title='Date Posted',
        yaxis_title='Number of Vacancies',
        legend_title='Clusters',
        template='plotly_white',
    )

    # Convert the Plotly figure to JSON for embedding in the template
    graph_json = fig.to_json()

    # Pass data and graph to the template
    context = {
        'graph_json': graph_json,
        'clustered_data': df.to_dict(orient='records'),
    }

    return render(request, 'pesostaff/job_vacancy_clustering_report.html', context)


def jobseeker_list(request):
    jobseekers = JobseekerProfile.objects.select_related(
        'user', 'resume'
    ).prefetch_related(
        'resume__education_entries',  # Ensure correct related name
        'resume__employment_entries',  # Ensure correct related name
    )

    jobseeker_data = []
    for jobseeker in jobseekers:
        phone = jobseeker.resume.phone
        educations = list(jobseeker.resume.education_entries.all())
        employments = list(jobseeker.resume.employment_entries.all())
        max_rows = max(len(educations), len(employments), 1)
        row_indexes = list(range(max_rows))
        educ_count = len(jobseeker.resume.education_entries.all())
        emp_count = len(jobseeker.resume.employment_entries.all())
        jobseeker.max_rows = max(educ_count, emp_count, 1)

        logger.info(f"Jobseeker: {jobseeker.user.first_name} - Phone: {jobseeker.resume.phone} - Educations: {educations} - Employments: {employments}")

        jobseeker_data.append({
            'jobseeker': jobseeker,
            'phone': phone,
            'educations': educations,
            'employments': employments,
            'max_rows': max_rows,
            'row_indexes': row_indexes,
            'educ_count': educ_count,
            'emp_count': emp_count,
            'jobseeker.max_rows': jobseeker.max_rows,
        })

    logger.info(f"Final jobseeker_data: {jobseeker_data}")
    return render(request, 'pesostaff/jobseeker_list.html', {'jobseekers': jobseeker_data})





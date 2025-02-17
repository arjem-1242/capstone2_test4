from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage, default_storage
from core.models import CustomUser
from employer.models import *

# Define custom file storage for documents
resume_document_storage = FileSystemStorage(location='media/resume_documents/')


from django.db import models
from django.utils import timezone

class Education(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name="education_history")
    resume = models.ForeignKey('ResumeDocument', on_delete=models.SET_NULL, null=True, default='', related_name="education_entries")

    # Data to be collected
    program = models.CharField(max_length=100, blank=True, null=True, default='')
    school = models.CharField(max_length=100, blank=True, null=True, default='')
    started = models.DateField(blank=True, null=True)
    finished = models.DateField(blank=True, null=True)

    def matches(self, data):
        return (
                self.program == data.get('program') and
                self.school == data.get('school') and
                self.started == data.get('started') and
                self.finished == data.get('finished')
        )


    def __str__(self):
        return f"{self.program} at {self.school} for {self.user.first_name}"

#
class Employment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name="employment_history")
    resume = models.ForeignKey('ResumeDocument', on_delete=models.SET_NULL, null=True, default='', related_name="employment_entries")

    # Data to be Collected
    role = models.CharField(max_length=100, blank=True, null=True, default='')
    company = models.CharField(max_length=100, blank=True, null=True, default='')
    hired = models.DateField(blank=True, null=True)
    resigned = models.DateField(blank=True, null=True)

    def matches(self, data):
        return (
            self.role == data.get('role') and
            self.company == data.get('company') and
            self.hired == data.get('hired') and
            self.resigned == data.get('resigned')
        )

    def __str__(self):
        return f"{self.role} at {self.company} for {self.user.first_name}"

#
class ResumeDocument(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="resume_documents", default='')

    # Data to be collected
    phone = models.TextField(blank=True, null=True, default='')
    skills = models.TextField(blank=True, null=True, default='')
    location = models.CharField(max_length=256, blank=True, null=True, default='')

    # Resume storage
    resume = models.FileField(upload_to="resume_document_storage", blank=True, null=True)

    # Parsing status
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    processed = models.BooleanField(default=False)

    # Status and Error Tracking
    status = models.CharField(max_length=20, default="Pending")  # e.g., "Pending", "Processing", "Completed", "Failed"
    error_message = models.TextField(blank=True, null=True)  # To log any processing errors

    # Optional Fields to Retain Processed Data for Reference
    raw_text = models.TextField(blank=True, null=True)  # Store raw OCR text for reference
    parsed_data = models.JSONField(blank=True, null=True)  # Store parsed details temporarily

    def __str__(self):
        return f"Resume for {self.user.first_name}"

    def get_resume(self):
        """Return a dictionary of document labels and their URLs."""
        return {"Resume": self.resume.url} if self.resume else {}

#
class JobseekerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, default='')

    location = models.CharField(max_length=256, blank=True, null=True, default='')
    contact = models.CharField(max_length=256, blank=True, null=True, default='')
    phone = models.CharField(max_length=256, blank=True, null=True, default='')

    resume = models.OneToOneField(ResumeDocument, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.user.first_name + self.user.last_name

class MatchedJobs(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default='')
    resume = models.ForeignKey(ResumeDocument, on_delete=models.CASCADE)
    job_posting = models.ForeignKey("employer.JobPosting", on_delete=models.CASCADE)
    matched_on = models.DateTimeField(default=timezone.now)

    # Fields for matched attributes
    matched_skills = models.TextField(blank=True, null=True)  # Stores matched skills as a comma-separated string
    matched_location = models.CharField(max_length=255, blank=True, null=True)  # Stores matched location as a string
    matched_position = models.CharField(max_length=255, blank=True, null=True)  # Stores the matched job position
    matched_education = models.TextField(blank=True, null=True)  # Stores matched education programs as a comma-separated string

    def __str__(self):
        return f"{self.user} matched with {self.job_posting.position}"

    def get_matched_skills(self):
        """Return matched skills as a list."""
        return self.matched_skills.split(',') if self.matched_skills else []

    def get_matched_education(self):
        """Return matched education programs as a list."""
        return self.matched_education.split(',') if self.matched_education else []

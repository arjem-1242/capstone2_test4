from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage, default_storage
from core.models import CustomUser

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

    # # Related models
    # educ = models.ForeignKey(Education, on_delete=models.SET_NULL, blank=True, null=True, related_name="resume_documents")
    # work = models.ForeignKey(Employment, on_delete=models.SET_NULL, blank=True, null=True, related_name="resume_documents")

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

    resume = models.OneToOneField(ResumeDocument, on_delete=models.CASCADE, default='')

    def __str__(self):
        return self.user.first_name + self.user.last_name

#
# class SavedJobs(models.Model):
#     job_posting = models.ForeignKey('JobPosting', on_delete=models.CASCADE, related_name='saved_jobs')
#     employer = models.ForeignKey('Employer', on_delete=models.CASCADE, related_name='saved_jobs')
#     date_saved = models.DateField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.applicant.user.username} saved for {self.job_posting.title}"
#
#
# class MatchedCandidate(models.Model):
#     job_posting = models.ForeignKey('JobPosting', on_delete=models.CASCADE, related_name='matched_candidates')
#     applicant = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='matched_candidates')
#     match_score = models.FloatField()  # Score indicating the degree of match based on OCR & NLP
#     matched_date = models.DateField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.applicant.user.username} matched with {self.job_posting.title} (Score: {self.match_score})"
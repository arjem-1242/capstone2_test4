
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage, default_storage
from core.models import CustomUser
from jobseeker.models import JobseekerProfile


# Define custom file storage for documents
applicant_document_storage = FileSystemStorage(location='media/applicant_documents/')
accreditation_document_storage = FileSystemStorage(location='media/accreditation_documents/')

class CompanyProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, default='')

    date_established = models.DateTimeField(default=timezone.now)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.company_name

class JobPosting(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, default='') #relates to a company

    position = models.CharField(max_length=255)
    job_description = models.TextField()
    date_posted = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    no_of_vacancies = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.position


class Applicant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='applicant_documents/', storage=applicant_document_storage)
    resume_text = models.TextField(blank=True, null=True)  # For OCR processed resume text
    applied_jobs = models.ManyToManyField('JobPosting', related_name='applicants')

    def __str__(self):
        return self.user.name

class AccreditationRequest(models.Model):
    COMPANY_TYPES = [
        ('Direct Company', 'Direct Company'),
        ('Manpower Agencies/Cooperative', 'Manpower Agencies/Cooperative'),
        ('For Overseas Manpower Agency', 'For Overseas Manpower Agency'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    company_profile = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, blank=True, null=True)  # Renamed field
    company = models.CharField(max_length=255)
    company_type = models.CharField(max_length=255, choices=COMPANY_TYPES, default='Direct Company')
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    comments = models.TextField(blank=True, null=True)
    document_text = models.TextField(blank=True, null=True)

    # Document fields
    sec_registration = models.FileField(upload_to='accreditation_documents/sec_registration/', blank=True, null=True)
    dti_permit = models.FileField(upload_to='accreditation_documents/dti_permit/', blank=True, null=True)
    business_permit = models.FileField(upload_to='accreditation_documents/business_permit/', blank=True, null=True)
    latest_job_posting = models.FileField(upload_to='accreditation_documents/latest_job_posting/', blank=True, null=True)
    latest_job_order_with_qualifications = models.FileField(upload_to='accreditation_documents/latest_job_order_with_qualifications/', blank=True, null=True)
    latest_payment_receipt = models.FileField(upload_to='accreditation_documents/latest_payment_receipt/', blank=True, null=True)
    no_pending_case_certificate = models.FileField(upload_to='accreditation_documents/no_pending_case_certificate/', blank=True, null=True)
    dole_permit = models.FileField(upload_to='accreditation_documents/dole_permit/', blank=True, null=True)
    bir_registration = models.FileField(upload_to='accreditation_documents/bir_registration/', blank=True, null=True)
    sss_membership_registration = models.FileField(upload_to='accreditation_documents/sss_membership_registration/', blank=True, null=True)
    tied_companies_list = models.FileField(upload_to='accreditation_documents/tied_companies_list/', blank=True, null=True)
    phil_job_net_registration = models.FileField(upload_to='accreditation_documents/phil_job_net_registration/', blank=True, null=True)
    poea_permit = models.FileField(upload_to='accreditation_documents/poea_permit/', blank=True, null=True)

    def __str__(self):
        return f"Accreditation Request for {self.company}"

    def get_documents(self):
        """Return a dictionary of document labels and their URLs."""
        document_labels = {
            'SEC Registration': self.sec_registration,
            'DTI Permit': self.dti_permit,
            'Business Permit': self.business_permit,
            'Latest Job Posting': self.latest_job_posting,
            'Latest Job Order with Qualifications': self.latest_job_order_with_qualifications,
            'Latest Payment Receipt': self.latest_payment_receipt,
            'No Pending Case Certificate': self.no_pending_case_certificate,
            'DOLE Permit': self.dole_permit,
            'BIR Registration': self.bir_registration,
            'SSS Membership Registration': self.sss_membership_registration,
            'Tied Companies List': self.tied_companies_list,
            'Phil Job Net Registration': self.phil_job_net_registration,
            'POEA Permit': self.poea_permit,
        }
        return {label: document for label, document in document_labels.items() if document}



class SavedCandidate(models.Model):
    job_posting = models.ForeignKey('JobPosting', on_delete=models.CASCADE, related_name='saved_candidates')
    applicant = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='saved_candidates')
    date_saved = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.user.first_name} saved for {self.job_posting.title}"


class MatchedCandidate(models.Model):
    job_posting = models.ForeignKey('JobPosting', on_delete=models.CASCADE, related_name='matched_candidates')
    applicant = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='matched_candidates')
    match_score = models.FloatField()  # Score indicating the degree of match based on OCR & NLP
    matched_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.user.first_name} matched with {self.job_posting.position} (Score: {self.match_score})"

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

    title = models.CharField(max_length=255)
    description = models.TextField()
    date_posted = models.DateField(auto_now_add=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='applicant_documents/', storage=applicant_document_storage)
    resume_text = models.TextField(blank=True, null=True)  # For OCR processed resume text
    applied_jobs = models.ManyToManyField('JobPosting', related_name='applicants')

    def __str__(self):
        return self.user.name

# class AccreditationRequest(models.Model):
#     COMPANY_TYPES = [
#         ('Direct Company', 'Direct Company'),
#         ('Manpower Agencies/Cooperative', 'Manpower Agencies/Cooperative'),
#         ('For Overseas Manpower Agency', 'For Overseas Manpower Agency'),
#     ]
#
#     STATUS_CHOICES = [
#         ('Pending', 'Pending'),
#         ('Approved', 'Approved'),
#         ('Rejected', 'Rejected'),
#     ]
#
#     company = models.CharField(max_length=255)
#     company_type = models.CharField(max_length=255, choices=COMPANY_TYPES, default='Direct Company')
#     request_date = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
#     comments = models.TextField(blank=True, null=True)
#
#     document_text = models.TextField(blank=True, null=True)
#
#     # Document fields
#     sec_registration = models.FileField(upload_to='accreditation_documents/sec_registration/', blank=True, null=True)
#     dti_permit = models.FileField(upload_to='accreditation_documents/dti_permit/', blank=True, null=True)
#     business_permit = models.FileField(upload_to='accreditation_documents/business_permit/', blank=True, null=True)
#     latest_job_posting = models.FileField(upload_to='accreditation_documents/latest_job_posting/', blank=True, null=True)
#     latest_job_order_with_qualifications = models.FileField(upload_to='accreditation_documents/latest_job_order_with_qualifications/', blank=True,null=True)
#     latest_payment_receipt = models.FileField(upload_to='accreditation_documents/latest_payment_receipt/', blank=True, null=True)
#     no_pending_case_certificate = models.FileField(upload_to='accreditation_documents/no_pending_case_certificate/', blank=True, null=True)
#     dole_permit = models.FileField(upload_to='accreditation_documents/dole_permit/', blank=True, null=True)
#     bir_registration = models.FileField(upload_to='accreditation_documents/bir_registration/', blank=True, null=True)
#     sss_membership_registration = models.FileField(upload_to='accreditation_documents/sss_membership_registration/', blank=True, null=True)
#     tied_companies_list = models.FileField(upload_to='accreditation_documents/tied_companies_list/', blank=True, null=True)
#     phil_job_net_registration = models.FileField(upload_to='accreditation_documents/phil_job_net_registration/', blank=True, null=True)
#     poea_permit = models.FileField(upload_to='accreditation_documents/poea_permit/', blank=True, null=True)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#         self.cleaned_data = None
#
#     def __str__(self):
#         return f"Accreditation Request for {self.company}"
#
#     def get_documents(self):
#         """Return a dictionary of document labels and their URLs."""
#         document_labels = {
#             'SEC Registration': self.sec_registration,
#             'DTI Permit': self.dti_permit,
#             'Business Permit': self.business_permit,
#             'Latest Job Posting': self.latest_job_posting,
#             'Latest Job Order with Qualifications': self.latest_job_order_with_qualifications,
#             'Latest Payment Receipt': self.latest_payment_receipt,
#             'No Pending Case Certificate': self.no_pending_case_certificate,
#             'DOLE Permit': self.dole_permit,
#             'BIR Registration': self.bir_registration,
#             'SSS Membership Registration': self.sss_membership_registration,
#             'Tied Companies List': self.tied_companies_list,
#             'Phil Job Net Registration': self.phil_job_net_registration,
#             'POEA Permit': self.poea_permit,
#         }
#         return {label: document for label, document in document_labels.items() if document}
#
#     def clean_document(self):
#             document = self.cleaned_data.get('document')
#
#             if document:
#                 # Check if the file is in memory or saved as a temporary file
#                 if hasattr(document, 'temporary_file_path'):
#                     # If the file is stored on disk, use its file path
#                     image = Image.open(document.temporary_file_path())
#                 else:
#                     # If the file is in-memory, use BytesIO to handle it
#                     image = Image.open(BytesIO(document.read()))
#
#                 # Convert the image into OpenCV format (BGR)
#                 image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#
#                 # Perform OCR to extract text using PyTesseract
#                 extracted_text = pytesseract.image_to_string(image_cv)
#                 self.cleaned_data['document_text'] = extracted_text  # Store the extracted text
#
#                 # Process the extracted text with spaCy
#                 doc = nlp(extracted_text)
#
#                 # Validate the presence of the company name in the extracted text
#                 company_name = self.cleaned_data.get('company')
#                 if company_name.lower() not in extracted_text.lower():
#                     raise forms.ValidationError("The uploaded document does not mention the company name.")
#
#             return document
#
#     def save(self, commit=True):
#         # Get the instance but don't save it yet
#         instance = super().save(commit=False)
#         # Assign the OCR extracted text to the document_text field in the model
#         instance.document_text = self.cleaned_data['document_text']
#         if commit:
#             instance.save()  # Save the instance only when commit=True
#         return instance

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
        return f"{self.applicant.user.first_username} matched with {self.job_posting.title} (Score: {self.match_score})"
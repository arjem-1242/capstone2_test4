from django.db import models
from employer.models import AccreditationRequest

class AccreditationRequestApproval(models.Model):
    accreditation_request = models.OneToOneField(AccreditationRequest, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)
    approved_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    uploaded_document = models.FileField(upload_to='approval_documents/', blank=True, null=True)

    def __str__(self):
        return f"Approval Status for {self.accreditation_request.company} - {'Approved' if self.approved else 'Rejected'}"

    def get_related_documents(self):
        """Return a dictionary of document labels and their URLs."""
        document_labels = {
            'SEC Registration': self.accreditation_request.sec_registration,
            'DTI Permit': self.accreditation_request.dti_permit,
            'Business Permit': self.accreditation_request.business_permit,
            'Latest Job Posting': self.accreditation_request.latest_job_posting,
            'Latest Job Order with Qualifications': self.accreditation_request.latest_job_order_with_qualifications,
            'Latest Payment Receipt': self.accreditation_request.latest_payment_receipt,
            'No Pending Case Certificate': self.accreditation_request.no_pending_case_certificate,
            'DOLE Permit': self.accreditation_request.dole_permit,
            'BIR Registration': self.accreditation_request.bir_registration,
            'SSS Membership Registration': self.accreditation_request.sss_membership_registration,
            'Tied Companies List': self.accreditation_request.tied_companies_list,
            'Phil Job Net Registration': self.accreditation_request.phil_job_net_registration,
            'POEA Permit': self.accreditation_request.poea_permit,
        }
        return {label: document for label, document in document_labels.items() if document}

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

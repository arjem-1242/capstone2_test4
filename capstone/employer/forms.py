import imghdr
import cv2
from PIL import Image, UnidentifiedImageError
import spacy
import numpy as np
import pytesseract
from django import forms
from django.core.exceptions import ValidationError
from .models import CompanyProfile, JobPosting, AccreditationRequest, Applicant, SavedCandidate
from io import BytesIO


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows

class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ['resume', 'applied_jobs']
        widgets = {
            'applied_jobs': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applied_jobs'].queryset = JobPosting.objects.all()


class CompanyProfileForm(forms.ModelForm):
    # Optional: If you want to display and edit CustomUser fields, define custom fields here
    email = forms.EmailField(required=True)
    company_name = forms.CharField(max_length=255, required=True)
    contact_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CompanyProfile
        fields = [ 'date_established', 'website']

    def __init__(self, *args, **kwargs):
        # Optionally pass a 'user' instance to prepopulate CustomUser data
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Prepopulate CustomUser fields if a user is provided
        if self.user:
            self.fields['email'].initial = self.user.email
            self.fields['company_name'].initial = self.user.company_name
            self.fields['contact_number'].initial = self.user.contact_number
            self.fields['address'].initial = self.user.address

    def save(self, commit=True):
        # Save CustomUser details first (email, company_name, etc.)
        user = self.user
        if user:
            user.email = self.cleaned_data['email']
            user.company_name = self.cleaned_data['company_name']
            user.contact_number = self.cleaned_data['contact_number']
            user.address = self.cleaned_data['address']
            user.save()

        # Then save CompanyProfile details
        company_profile = super().save(commit=False)
        company_profile.user = user  # Link to the CustomUser instance
        if commit:
            company_profile.save()
        return company_profile

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'salary', 'qualifications', 'requirements']

nlp = spacy.load("en_core_web_sm")

# class AccreditationRequestForm(forms.ModelForm):
#     class Meta:
#         model = AccreditationRequest
#         fields = [
#             'company', 'company_type', 'sec_registration', 'dti_permit', 'business_permit',
#             'latest_job_posting', 'no_pending_case_certificate', 'dole_permit',
#             'bir_registration', 'tied_companies_list', 'phil_job_net_registration', 'poea_permit', 'latest_job_order_with_qualifications',
#             'latest_payment_receipt', 'sss_membership_registration',
#         ]
#         widgets = {
#             'company_type': forms.Select(choices=AccreditationRequest.COMPANY_TYPES),
#             'sec_registration': forms.ClearableFileInput(attrs={'multiple': False}),
#             'dti_permit': forms.ClearableFileInput(attrs={'multiple': False}),
#             'business_permit': forms.ClearableFileInput(attrs={'multiple': False}),
#             'latest_job_posting': forms.ClearableFileInput(attrs={'multiple': False}),
#             'latest_job_order_with_qualifications': forms.ClearableFileInput(attrs={'multiple': False}),
#             'latest_payment_receipt': forms.ClearableFileInput(attrs={'multiple': False}),
#             'no_pending_case_certificate': forms.ClearableFileInput(attrs={'multiple': False}),
#             'dole_permit': forms.ClearableFileInput(attrs={'multiple': False}),
#             'bir_registration': forms.ClearableFileInput(attrs={'multiple': False}),
#             'sss_membership_registration': forms.ClearableFileInput(attrs={'multiple': False}),
#             'tied_companies_list': forms.ClearableFileInput(attrs={'multiple': False}),
#             'phil_job_net_registration': forms.ClearableFileInput(attrs={'multiple': False}),
#             'poea_permit': forms.ClearableFileInput(attrs={'multiple': False}),
#         }
#
#         def save(self, commit=True):
#             instance = super().save(commit=False)
#
#             file_fields = [
#                 'sec_registration', 'dti_permit', 'business_permit', 'latest_job_posting',
#                 'no_pending_case_certificate', 'dole_permit', 'bir_registration',
#                 'tied_companies_list', 'phil_job_net_registration', 'poea_permit', 'latest_job_order_with_qualifications',
#                 'latest_payment_receipt', 'sss_membership_registration',
#             ]
#
#             for field_name in file_fields:
#                 file = self.cleaned_data.get(field_name)  # Access cleaned_data in the save method
#                 if file:
#                     try:
#                         # Perform OCR on the file
#                         image = Image.open(file)
#                         extracted_text = pytesseract.image_to_string(image)
#
#                         # Save the extracted text into the corresponding field in the instance
#                         text_field_name = field_name + '_text'
#                         setattr(instance, text_field_name, extracted_text)
#
#                     except Exception as e:
#                         raise ValidationError(
#                             f"Error extracting text from {field_name.replace('_', ' ').capitalize()}: {str(e)}")
#
#             if commit:
#                 instance.save()
#
#             return instance

class AccreditationRequestForm(forms.ModelForm):
    class Meta:
        model = AccreditationRequest
        fields = ['company', 'company_type', 'comments', 'sec_registration', 'dti_permit', 'business_permit', 'latest_job_posting',
                  'latest_job_order_with_qualifications', 'latest_payment_receipt', 'no_pending_case_certificate', 'dole_permit',
                  'bir_registration', 'sss_membership_registration', 'tied_companies_list', 'phil_job_net_registration', 'poea_permit']
        widgets = {
            'company_type': forms.Select(choices=AccreditationRequest.COMPANY_TYPES),
        }

    # def clean_document(self):
    #     # This method can be customized to handle specific document validation if needed.
    #     # If you want to handle multiple documents, you should implement separate methods or handle them accordingly.
    #     return super().clean_document()

    def clean(self):
        cleaned_data = super().clean()
        # Handle OCR and NLP processing
        for field in ['sec_registration', 'dti_permit', 'business_permit', 'latest_job_posting',
                      'latest_job_order_with_qualifications', 'latest_payment_receipt', 'no_pending_case_certificate',
                      'dole_permit', 'bir_registration', 'sss_membership_registration', 'tied_companies_list',
                      'phil_job_net_registration', 'poea_permit']:
            document = cleaned_data.get(field)
            if document:
                # Check if the file is in memory or saved as a temporary file
                if hasattr(document, 'temporary_file_path'):
                    # If it's a file on disk, use the file path
                    image = Image.open(document.temporary_file_path())
                else:
                    # If it's an in-memory file, use BytesIO
                    image = Image.open(BytesIO(document.read()))

                # Convert the image to OpenCV format for processing
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Use PyTesseract to extract text from the image
                extracted_text = pytesseract.image_to_string(image_cv)
                self.instance.document_text = extracted_text  # Save the extracted text to the model instance

                # Use spaCy to process the extracted text
                doc = nlp(extracted_text)

                # Check if the company name is mentioned in the document
                company_name = cleaned_data.get('company')
                if company_name.lower() not in extracted_text.lower():
                    self.add_error(field, "The uploaded document does not contain the company name.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class SavedCandidateForm(forms.ModelForm):
    class Meta:
        model = SavedCandidate
        fields = ['job_posting', 'applicant']



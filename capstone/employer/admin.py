from django.contrib import admin

from django import forms

from employer.forms import JobPostingForm
from employer.models import *

from core.models import *

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    # Add custom methods to display fields from the related CustomUser
    list_display = ('user', 'email', 'company_name', 'date_established', 'website')
    # list_display = ('user', 'email', 'company_name', 'contact_number', 'address', 'industry', 'date_established', 'website')


    # Custom method to display the email from the related CustomUser
    def email(self, obj):
        return obj.user.email

    # Custom method to display the name from the related CustomUser
    def company_name(self, obj):
        return obj.user.company_name

    # # Custom method to display the contact number from the related CustomUser
    # def contact_number(self, obj):
    #     return obj.user.contact_number
    #
    # # Custom method to display the address from the related CustomUser
    # def address(self, obj):
    #     return obj.user.address

    # Optional: Give friendly column headers in the admin interface
    email.short_description = 'Email'
    company_name.short_description = 'Name'
    # contact_number.short_description = 'Contact Number'
    # address.short_description = 'Address'

@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    form = JobPostingForm
    list_display = ('position', 'date_posted', 'salary')
    search_fields = ('position', 'skills', 'location')
    list_filter = ('date_posted',)
    ordering = ('-date_posted',)

@admin.register(AccreditationRequest)
class AccreditationRequestAdmin(admin.ModelAdmin):
    list_display = ('company', 'company_type', 'request_date', 'status')
    list_filter = ('status', 'company_type')
    search_fields = ('company_name',)

    formfield_overrides = {
        models.CharField: {'widget': forms.Select},  # Apply Select widget to CharField
    }

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'company_type':
            kwargs['widget'] = forms.Select(choices=AccreditationRequest.COMPANY_TYPES)
        if db_field.name == 'status':
            kwargs['widget'] = forms.Select(choices=AccreditationRequest.STATUS_CHOICES)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('user', 'resume')
    search_fields = ('user__first_name',) # changed from username
    ordering = ('user__first_name',) #changed from username

@admin.register(SavedCandidate)
class SavedCandidateAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_posting', 'date_saved')
    search_fields = ('applicant__user__username', 'job_posting__title')
    list_filter = ('date_saved',)
    ordering = ('-date_saved',)
    raw_id_fields = ('applicant', 'job_posting')

@admin.register(MatchedCandidate)
class MatchedCandidateAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job_posting', 'match_score', 'matched_date')
    search_fields = ('applicant__user__username', 'job_posting__position')
    list_filter = ('matched_date',)
    ordering = ('-matched_date',)
    raw_id_fields = ('applicant', 'job_posting')

# Register your models here.

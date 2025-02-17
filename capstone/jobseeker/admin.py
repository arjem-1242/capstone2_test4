from django.contrib import admin

from django import forms

from employer.forms import JobPostingForm
from employer.models import *

from core.models import *
from jobseeker.models import JobseekerProfile


@admin.register(JobseekerProfile)
class JobseekerProfileAdmin(admin.ModelAdmin):
    # Add custom methods to display fields from the related CustomUser
    list_display = ('user', 'email', 'first_name', 'middle_name', 'last_name')

    # Custom method to display the email from the related CustomUser
    def email(self, obj):
        return obj.user.email

    # Custom method to display the name from the related CustomUser
    def first_name(self, obj):
        return obj.user.first_name

    def middle_name(self, obj):
        return obj.user.middle_name

    def last_name(self, obj):
        return obj.user.last_name

    # # Custom method to display the contact number from the related CustomUser
    # def contact_number(self, obj):
    #     return obj.user.contact_number
    #
    # # Custom method to display the address from the related CustomUser
    # def address(self, obj):
    #     return obj.user.address

    # Optional: Give friendly column headers in the admin interface
    email.short_description = 'Email'
    first_name.short_description = 'First Name'
    middle_name.short_description = 'Middle Name'
    last_name.short_description = 'Last Name'


class MatchedJob(admin.ModelAdmin):
    # Add custom methods to display fields from the related CustomUser
    list_display = ('job_seeker', 'job_posting', 'match_score')

    # Custom method to display the email from the related CustomUser
    def job_seeker(self, obj):
        return obj.matchedjob.job_seeker

    # Custom method to display the name from the related CustomUser
    def job_posting(self, obj):
        return obj.matchedjob.job_posting

    def match_score(self, obj):
        return obj.matchedjob.match_score


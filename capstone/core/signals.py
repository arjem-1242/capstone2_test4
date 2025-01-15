# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from pygments.lexer import default

from jobseeker.models import JobseekerProfile, ResumeDocument, Education, Employment
from .models import CustomUser
from employer.models import CompanyProfile
from django.db.models.signals import post_save
from django.dispatch import receiver



@receiver(post_save, sender=CustomUser)
def create_company_profile(instance, created, **kwargs):
    # Only create CompanyProfile for Employers
    if created and instance.user_type == 'EMPLOYER':
        CompanyProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def create_jobseeker_profile(instance, created, **kwargs):
    if created and instance.user_type == 'JOB_SEEKER':
        # Check if a JobseekerProfile already exists for this user
        if not JobseekerProfile.objects.filter(user=instance).exists():
            with transaction.atomic():



                # Create resume document
                resume_document = ResumeDocument.objects.create(user=instance)

                # Create related objects
                educ = Education.objects.create(user=instance, resume=resume_document)
                work = Employment.objects.create(user=instance, resume=resume_document)


                # Create JobseekerProfile
                JobseekerProfile.objects.create(user=instance, resume=resume_document)

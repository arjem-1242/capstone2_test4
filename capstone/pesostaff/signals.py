from django.db.models.signals import post_save
from django.dispatch import receiver
from pesostaff.models import AccreditationRequestApproval

@receiver(post_save, sender=AccreditationRequestApproval)
def update_accreditation_status(sender, instance, **kwargs):
    accreditation_request = instance.accreditation_request
    accreditation_request.status = 'Approved' if instance.approved else 'Rejected'
    accreditation_request.save()

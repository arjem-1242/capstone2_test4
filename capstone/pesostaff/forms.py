from django import forms
from .models import AccreditationRequestApproval
from .models import Event

class AccreditationRequestApprovalForm(forms.ModelForm):
    class Meta:
        model = AccreditationRequestApproval
        fields = ['approved', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'location', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

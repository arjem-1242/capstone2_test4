from django import forms
from .models import AccreditationRequestApproval

class AccreditationRequestApprovalForm(forms.ModelForm):
    class Meta:
        model = AccreditationRequestApproval
        fields = ['approved', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }

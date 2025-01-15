from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser

class PESOStaffRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'staff_code']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'PESO'
        if commit:
            user.save()
        return user
    
class PESOStaffLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.user_type != 'PESO':
            raise forms.ValidationError("This account does not have PESO Staff privileges.", code='invalid_login')


class EmployerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'company_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'EMPLOYER'
        if commit:
            user.save()
        return user

class EmployerLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.user_type != 'EMPLOYER':
            raise forms.ValidationError("This account does not have Employer privileges.", code='invalid_login')


class JobSeekerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'middle_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'JOB_SEEKER'
        if commit:
            user.save()
        return user
    
class JobSeekerLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if user.user_type != 'JOB_SEEKER':
            raise forms.ValidationError("This account does not have Job Seeker privileges.", code='invalid_login')


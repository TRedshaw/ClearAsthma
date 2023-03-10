from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth.forms import UserCreationForm

from Clear.models import AppUser, Boroughs


class LoginForm(auth_forms.AuthenticationForm):
    class Meta(UserCreationForm):
        model = AppUser

    # Specify the widgets and CSS classes to be applied to the form tags
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username','placeholder':'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password','placeholder':'Password'}))


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = AppUser
        fields = UserCreationForm.Meta.fields + ('dob', 'pollution_limit', 'consent')

    # Specify the widgets and CSS classes to be applied to the form tags
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control ',
                  'id': 'username',
                  'placeholder': 'Username'}))

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control',
                  'id': 'password1',
                  'placeholder': 'Password'}))

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control mb-3',
                  'id': 'password2',
                  'placeholder': 'Password Confirmation'}))

    dob = forms.DateField(
        widget = forms.DateInput(
            attrs={'class': 'form-control',
                   'type': 'text',
                   'onfocus':"(this.type='date')",
                   'placeholder': 'Date of Birth'}))

    pollution_limit = forms.IntegerField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'text',
                   'onfocus': "(this.type='number')",
                   'placeholder': 'Pollution Limit',
                   'min': 0,
                   'max': 10}))

    consent = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={'class': 'form-check-input',
                   'type': 'checkbox'}))


# SettingsForm allows the user to enter required data that is then sent to the server for processing
class SettingsForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'id': 'username', 'placeholder': 'Username'}))
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'id': 'surname', 'placeholder': 'First Name'}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', 'id': 'surname', 'placeholder': 'Surname'}))
    # Specify ModelChoice because this is a ForeignKey field so we can automatically display it as a SELECT tag and populate the choices from the database
    home_borough = forms.ModelChoiceField(required=False,queryset=Boroughs.objects.all(), empty_label="None", widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    work_borough = forms.ModelChoiceField(required=False,queryset=Boroughs.objects.all(), empty_label="None", widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    other_borough = forms.ModelChoiceField(required=False,queryset=Boroughs.objects.all(), empty_label="None", widget=forms.Select(attrs={'class': 'form-control form-control-sm'}))
    # Setting up pollution limit from the settings page
    pollution_limit = forms.IntegerField(
        widget=forms.TextInput(
            attrs={'class': 'form-control',
                   'type': 'text',
                   'onfocus': "(this.type='number')",
                   'placeholder': 'Pollution Limit',
                   'min': 0,
                   'max': 10}))

    class Meta:
        model = AppUser
        fields=['username','first_name','last_name','home_borough','work_borough','other_borough','pollution_limit']

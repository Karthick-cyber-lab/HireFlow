from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML
from .models import CustomUser, UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'your@email.com'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    role = forms.ChoiceField(
        choices=[('applicant', 'Job Seeker'), ('recruiter', 'Recruiter')],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'username', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'email',
            'username',
            'role',
            'password1',
            'password2',
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100 mt-3'),
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.get_or_create(user=user)
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'autofocus': True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Sign In', css_class='btn btn-primary w-100 mt-3'),
        )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'phone', 'location', 'linkedin_url', 'github_url',
                  'portfolio_url', 'resume', 'avatar', 'skills', 'experience_years']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Python, Django, React, ...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'bio',
            Row(
                Column('phone', css_class='col-md-6'),
                Column('location', css_class='col-md-6'),
            ),
            Row(
                Column('experience_years', css_class='col-md-4'),
                Column('skills', css_class='col-md-8'),
            ),
            Row(
                Column('linkedin_url', css_class='col-md-6'),
                Column('github_url', css_class='col-md-6'),
            ),
            'portfolio_url',
            Row(
                Column('avatar', css_class='col-md-6'),
                Column('resume', css_class='col-md-6'),
            ),
            Submit('submit', 'Update Profile', css_class='btn btn-primary mt-3'),
        )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

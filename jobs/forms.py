from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import Job, JobCategory


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'company', 'company_logo', 'location',
            'job_type', 'experience_level', 'description', 'requirements',
            'responsibilities', 'salary_min', 'salary_max',
            'skills_required', 'vacancies', 'deadline', 'status', 'is_featured',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
            'responsibilities': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'skills_required': forms.TextInput(attrs={'placeholder': 'Python, Django, REST API, ...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset('Job Details',
                Row(
                    Column('title', css_class='col-md-8'),
                    Column('category', css_class='col-md-4'),
                ),
                Row(
                    Column('company', css_class='col-md-6'),
                    Column('location', css_class='col-md-6'),
                ),
                'company_logo',
            ),
            Fieldset('Job Type & Experience',
                Row(
                    Column('job_type', css_class='col-md-4'),
                    Column('experience_level', css_class='col-md-4'),
                    Column('vacancies', css_class='col-md-4'),
                ),
            ),
            Fieldset('Description',
                'description', 'requirements', 'responsibilities',
            ),
            Fieldset('Compensation & Skills',
                Row(
                    Column('salary_min', css_class='col-md-6'),
                    Column('salary_max', css_class='col-md-6'),
                ),
                'skills_required',
            ),
            Fieldset('Publishing',
                Row(
                    Column('deadline', css_class='col-md-4'),
                    Column('status', css_class='col-md-4'),
                    Column('is_featured', css_class='col-md-4 d-flex align-items-end'),
                ),
            ),
            Submit('submit', 'Save Job', css_class='btn btn-primary mt-3'),
        )


class JobSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Job title, skill, company...', 'class': 'form-control'}),
    )
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Job.TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'City or Remote', 'class': 'form-control'}),
    )
    experience = forms.ChoiceField(
        choices=[('', 'All Levels')] + Job.EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

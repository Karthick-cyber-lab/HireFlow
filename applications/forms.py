from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Application, Interview


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Tell us why you are a great fit for this role...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'cover_letter',
            'resume',
            Submit('submit', 'Submit Application', css_class='btn btn-primary w-100 mt-3'),
        )


class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'recruiter_notes']
        widgets = {
            'recruiter_notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Internal notes...'}),
        }

    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Reason for this status change (visible in history)...'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'status', 'recruiter_notes', 'note',
            Submit('submit', 'Update Status', css_class='btn btn-primary'),
        )


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['scheduled_at', 'duration_minutes', 'mode', 'interviewer_name',
                  'meeting_link', 'venue', 'notes', 'result', 'feedback']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('scheduled_at', css_class='col-md-6'),
                Column('duration_minutes', css_class='col-md-3'),
                Column('mode', css_class='col-md-3'),
            ),
            Row(
                Column('interviewer_name', css_class='col-md-6'),
                Column('meeting_link', css_class='col-md-6'),
            ),
            'venue', 'notes',
            Row(
                Column('result', css_class='col-md-4'),
                Column('feedback', css_class='col-md-8'),
            ),
            Submit('submit', 'Save Interview', css_class='btn btn-primary'),
        )

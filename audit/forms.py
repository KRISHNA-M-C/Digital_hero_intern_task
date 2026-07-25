from django import forms
from django.core.exceptions import ValidationError

class UrlAuditForm(forms.Form):
    url = forms.URLField(
        required=True,
        error_messages={
            'required': 'URL is required.',
            'invalid': 'Please enter a valid URL (including http:// or https://).'
        }
    )

    def clean_url(self):
        url = self.cleaned_data.get('url')
        # Ensure it starts with http or https
        if url and not (url.startswith('http://') or url.startswith('https://')):
            raise ValidationError('URL must start with http:// or https://.')
        return url

from django import forms
from profiles.validators import validate_file


class ProfileForm(forms.Form):
    company = forms.CharField()
    company_description = forms.CharField()
    company_linkedin = forms.URLField()
    company_website = forms.URLField()
    company_metadata = forms.CharField()
    company_members = forms.CharField()
    firstname = forms.CharField()
    lastname = forms.CharField()
    url = forms.URLField()
    position = forms.CharField()

    def clean_company(self, data):
        return data
    

class FileUploadForm(forms.Form):
    profiles = forms.FileField(validators=[validate_file])


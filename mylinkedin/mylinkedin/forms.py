from django import forms
from mylinkedin.validators import validate_file

class LinkedinFileUploadForm(forms.Form):
    profiles = forms.FileField(validators=[validate_file])

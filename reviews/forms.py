from django import forms

from profiles.validators import validate_file


class ReviewsFileUploadForm(forms.Form):
    reviews = forms.FileField(validators=[validate_file])

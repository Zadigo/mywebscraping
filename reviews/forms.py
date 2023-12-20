from django import forms

from profiles.validators import validate_file


class ReviewsFileUploadForm(forms.Form):
    reviews = forms.FileField(validators=[validate_file])


class SearchForm(forms.Form):
    search = forms.CharField(max_length=200, validators=[], required=True)


class StartRobotForm(forms.Form):
    url = forms.URLField(validators=[], required=True)

    def validate_url(self, data):
        return data

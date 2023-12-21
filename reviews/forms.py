from django import forms

from reviews.validators import validate_file


class ReviewsFileUploadForm(forms.Form):
    """Form to upload a file containing  a set of reviews.
    Optionnally a company name can be provided to overide
    the one provided in the file"""

    company_name = forms.CharField(required=False)
    reviews_file = forms.FileField(validators=[validate_file])

    def clean_business_name(self):
        cleaned_data = self.cleaned_data
        cleaned_data['business_name'] = name.capitalize()
        return cleaned_data


class SearchForm(forms.Form):
    search = forms.CharField(max_length=200, validators=[], required=True)


class StartRobotForm(forms.Form):
    url = forms.URLField(validators=[], required=True)

    def clean_url(self, data):
        return data

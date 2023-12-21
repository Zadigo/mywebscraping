import pandas
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import FormView, TemplateView

from mywebscraping import forms
from profiles import utils
from reviews.models import Company, Review


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        number_of_companies = Company.objects.count()
        context['number_of_companies'] = number_of_companies
        
        number_of_reviews = Review.objects.count()
        context['number_of_reviews'] = number_of_reviews
        return context
    

# class UploadFileView(FormView):
#     form_class = forms.LinkedinFileUploadForm
#     template_name = 'upload.html'
#     success_url = reverse_lazy('file_upload')
#     expected_columns = {
#         'company',
#         'company_description',
#         'company_linkedin',
#         'company_members',
#         'company_metadata',
#         'enriched',
#         'first_name',
#         'full_name',
#         'last_name',
#         'linkedin',
#         'position',
#         'source',
#         'website'
#     }

#     def form_valid(self, form):
#         from nltk.tokenize import LineTokenizer

#         file = form.cleaned_data['profiles']

#         new_filename = get_random_string(length=5)
#         if file.content_type == 'text/csv':
#             df = pandas.read_csv(file)
#             # new_file_path = settings.MEDIA_ROOT / f'{new_filename}.csv'
#             # df.to_csv(new_file_path, index=False)
#         else:
#             df = pandas.read_json(file)
#             # new_file_path = settings.MEDIA_ROOT / f'{new_filename}.json'
#             # df.to_json(new_file_path, force_ascii=False, orient='records')

#         missing_columns = self.expected_columns.difference(set(df.columns))
#         if missing_columns:
#             form.add_error(None, f'Missing columns: {list(missing_columns)}')
#             return super().form_invalid(form)

#         df = df.sort_values('last_name')
#         df = df.drop_duplicates(subset=['first_name', 'last_name'])

#         def normalize_name(value):
#             return str(value).lower().title()

#         columns_to_normalize = ['last_name', 'first_name']

#         for column in columns_to_normalize:
#             df[column] = df[column].apply(normalize_name)

#         tokenizer = LineTokenizer()
#         for item in df.itertuples():
#             if item.company_description is not None:
#                 try:
#                     tokens = tokenizer.tokenize(item.company_description)
#                 except:
#                     pass
#                 else:
#                     df.loc[item.Index, 'company_description'] = ' '.join(
#                         tokens)

#         df['company'] = df['company'].apply(utils.extract_company)
#         df['of_interest'] = df['position'].map(utils.test_profile_position)

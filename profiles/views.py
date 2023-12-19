import os
from audioop import reverse
from typing import Any

import dotenv
import pandas
import requests
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, View
from django.shortcuts import redirect

from profiles import utils
from profiles.forms import FileUploadForm, ProfileForm
from profiles.models import Company, LinkedinProfile


class CompaniesView(ListView):
    model = Company
    queryset = Company.objects.all()
    template_name = 'profiles/list_companies.html'
    context_object_name = 'companies'


class CompanyView(DetailView):
    model = Company
    queryset = Company.objects.all()
    template_name = 'profiles/explore.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search = self.request.GET.get('search')
        position = self.request.GET.get('position')
        interest = self.request.GET.get('interest')

        company = self.get_object()
        profiles = company.linkedinprofile_set.annotate(
            lowered_position=Lower('position'))

        disable_undo_button = True

        if search is not None:
            profiles = profiles.filter(
                Q(firstname__icontains=search) |
                Q(lastname__icontains=search)
            )
            disable_undo_button = False

        if position is not None:
            profiles = profiles.filter(position__icontains=position)
            disable_undo_button = False

        if interest is not None:
            profiles = profiles.filter(of_interest=True)
            disable_undo_button = False

        context['profiles'] = profiles
        context['searched_search'] = search or ''
        context['searched_position'] = position or ''
        context['searched_interest'] = interest
        print(interest)
        context['disable_undo_button'] = disable_undo_button
        return context


class CreateProfileView(FormView):
    form_class = ProfileForm
    template_name = 'profiles/upload.html'

    def form_valid(self, form):
        company_details = {
            'name': form.cleaned_data['company'],
            'description': form.cleaned_data['company'],
            'website': form.cleaned_data['company'],
            'linkedin': form.cleaned_data['company'],
            'metadata': form.cleaned_data['company'],
            'members': form.cleaned_data['company']
        }
        instance, state = Company.objects.get_or_create(**company_details)

        profile_details = {
            'firstname': form.cleaned_data['firstname'],
            'lastname': form.cleaned_data['lastname'],
            'url': form.cleaned_data['url'],
            'position': form.cleaned_data['position']
        }
        profile = instance.objects.create(**profile_details)
        return super().form_valid(form)


class UploadFileView(FormView):
    form_class = FileUploadForm
    template_name = 'profiles/upload.html'
    success_url = reverse_lazy('uploads:file_upload')
    expected_columns = {
        'company',
        'company_description',
        'company_linkedin',
        'company_members',
        'company_metadata',
        'enriched',
        'first_name',
        'full_name',
        'last_name',
        'linkedin',
        'position',
        'source',
        'website'
    }

    def form_valid(self, form):
        from nltk.tokenize import LineTokenizer

        file = form.cleaned_data['profiles']

        new_filename = get_random_string(length=5)
        if file.content_type == 'text/csv':
            df = pandas.read_csv(file)
            # new_file_path = settings.MEDIA_ROOT / f'{new_filename}.csv'
            # df.to_csv(new_file_path, index=False)
        else:
            df = pandas.read_json(file)
            # new_file_path = settings.MEDIA_ROOT / f'{new_filename}.json'
            # df.to_json(new_file_path, force_ascii=False, orient='records')

        missing_columns = self.expected_columns.difference(set(df.columns))
        if missing_columns:
            form.add_error(None, f'Missing columns: {list(missing_columns)}')
            return super().form_invalid(form)

        df = df.sort_values('last_name')
        df = df.drop_duplicates(subset=['first_name', 'last_name'])

        def normalize_name(value):
            return str(value).lower().title()

        columns_to_normalize = ['last_name', 'first_name']

        for column in columns_to_normalize:
            df[column] = df[column].apply(normalize_name)

        tokenizer = LineTokenizer()
        for item in df.itertuples():
            if item.company_description is not None:
                try:
                    tokens = tokenizer.tokenize(item.company_description)
                except:
                    pass
                else:
                    df.loc[item.Index, 'company_description'] = ' '.join(
                        tokens)

        df['company'] = df['company'].apply(utils.extract_company)
        df['of_interest'] = df['position'].map(utils.test_profile_position)

        # company_cache = {}
        # unique_companies = df[df.duplicated(subset=['company']) == False]
        # unique_companies = unique_companies[['company', 'company_description',
        #                                  'company_linkedin', 'company_members', 'company_metadata']]
        
        # for item in unique_companies.itertuples(name='Profile'):
        #     try:
        #         company, state = Company.objects.get_or_create(
        #             name=unique_companies.company,
        #             defaults={
        #                 'description': unique_companies.company_description,
        #                 'website': unique_companies.website,
        #                 'linkedin': unique_companies.company_linkedin,
        #                 'metadata': unique_companies.company_metadata,
        #                 'members': unique_companies.company_members
        #             }
        #         )
        #         company_cache[company.name] = company
        #     except Exception as e:
        #         break

        for item in df.itertuples(name='Profile'):
            try:
                company, state = Company.objects.get_or_create(
                    name=item.company,
                    defaults={
                        'description': item.company_description,
                        'website': item.website,
                        'linkedin': item.company_linkedin,
                        'metadata': item.company_metadata,
                        'members': item.company_members
                    }
                )
            except Exception as e:
                break

            try:
                profile, state = company.linkedinprofile_set.get_or_create(
                    firstname=item.first_name,
                    lastname=item.last_name,
                    defaults={
                        'url': item.linkedin,
                        'of_interest': item.of_interest,
                        'position': item.position
                    }
                )
            except Exception as e:
                pass

        return super().form_valid(form)


@require_POST
async def enrcich_view(request, **kwargs):
    url = 'https://api.dropcontact.io/batch'
    headers = {'X-Access-Token': os.getenv('DROPCONTACT')}

    email = request.POST.get('email')
    firstname = request.POST.get('firstname')
    lastname = request.POST.get('lastname')

    try:
        profile = LinkedinProfile.objects.filter(email=email)
    except:
        return redirect(reverse('uploads:profiles'))

    async def authenticate():
        try:
            response = requests.post(
                url,
                headers=headers
            )
        except:
            return {}
        else:
            return response.json()

    async def enrich_data():
        headers.update({'Content-Type': 'application/json'})
        try:
            response = requests.post(
                url,
                data=[
                    {
                        'email': email,
                        'firstname': firstname,
                        'lastname': lastname
                    }
                ],
                headers=headers
            )
        except:
            return {}
        else:
            return response.json()

    data = await authenticate()
    print(data)
    await enrich_data(data['request_id'])
    return redirect(reverse('uploads:profiles'))

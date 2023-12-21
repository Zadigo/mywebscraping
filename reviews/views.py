import asyncio
import csv
import json
import logging
import subprocess

import pandas
from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.messages import add_message
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Length
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, View

from mywebscraping.utils import create_filename
from reviews import utils
from reviews.forms import ReviewsFileUploadForm, SearchForm, StartRobotForm
from reviews.machine_learning.sentiment import CalculateSentiment
from reviews.models import Company, Review
from reviews.utils import (clean_company_dictionnary,
                           parse_number_of_reviews, parse_rating)


def create_download_http_response(request, dataframe, file_prefix=None, file_suffix=None):
    """Writes the results of a dataframe to an 
    HTTPResponse object so that the user can download
    a csv file"""
    filename = create_filename(prefix=file_prefix, suffix=file_suffix)
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}.csv"'
        }
    )
    response.write(dataframe.to_csv(index=False, encoding='utf-8'))
    return response


class ListCompaniesView(ListView):
    """Shows the list of companies stored
    in the current database"""

    model = Company
    queryset = Company.objects.all()
    template_name = 'reviews/pages/list_companies.html'
    context_object_name = 'companies'
    search_form_class = SearchForm

    def get_queryset(self):
        queryset = super().get_queryset()
        form = self.search_form_class(self.request.GET)
        if form.is_valid():
            search = form.cleaned_data['search']
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(address__icontains=search)
            )
        return queryset


class ListReviewsView(DetailView):
    """Shows the reviews for a specific
    given company of the database"""

    model = Company
    queryset = Company.objects.all()
    template_name = 'reviews/pages/reviews.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        by_text_length = self.request.GET.get('text')
        rating_sort = self.request.GET.get('rating')

        company = self.get_object()
        reviews = company.review_set.all()

        if by_text_length == 1:
            queryset = reviews.annotate(text_length=Length('text'))
            reviews = queryset.order_by('-text_length')

        accepted_sorts = ['asc', 'desc']
        if rating_sort is not None and rating_sort in accepted_sorts:
            column = 'rating' if rating_sort == 'asc' else '-rating'
            reviews = reviews.order_by(column)

        context['reviews'] = reviews
        return context


# @method_decorator(cache_page(1 * 60), method='dispatch')
class UploadReviewsView(FormView):
    """Upload a file containing Google reviews
    directly to the database using a form"""

    form_class = ReviewsFileUploadForm
    success_url = reverse_lazy('reviews:list_companies')
    template_name = 'reviews/pages/upload.html'

    def create_reviews(self, instance, reviews):
        """Bulk create reviews which is a quicker more
        efficient method than using the foreign key"""
        r1 = utils.clean_reviews_text(reviews)
        r2 = utils.parse_rating(r1)
        cleaned_reviews = utils.parse_number_of_reviews(r2)

        new_reviews_objs = []
        for cleaned_review in cleaned_reviews:
            review = Review(
                review_id=utils.create_id('rev'),
                company=instance,
                **cleaned_review
            )
            new_reviews_objs.append(review)

        objs = Review.objects.bulk_create(new_reviews_objs)

    def form_valid(self, form):
        provided_company_name = form.cleaned_data.get('company_name')
        file = form.cleaned_data['reviews_file']

        content = json.loads(file.read())

        result = utils.validate_file_integrity(content)
        if result:
            columns = ', '.join(result)
            form.add_error(None, f"Your file is missing the required columns: {columns}")
            return super().form_invalid(form)

        result = utils.validate_file_reviews(content)
        if result:
            columns = ', '.join(result)
            form.add_error(
                None, 
                f"One of your review dictionnary is "
                f"missing the required columns: {columns}"
            )
            return super().form_invalid(form)

        if isinstance(content, list):
            # Associate each company with the
            # reviews that should be created
            # for it's model instance
            instances = {}
            for company_details in content:
                reviews = company_details.pop('reviews')
                company_details.pop('date')
                company_details.pop('number_of_reviews')
                clean_company_details = utils.clean_company_dictionnary(company_details)
                company_name = clean_company_details.pop('name')

                instance, _ = Company.objects.get_or_create(
                    name=company_name,
                    defaults=clean_company_details
                )
                # Save the file that was used
                # to upload the reviews
                instance.reviews_file = file
                instance.save()

                instances[instance] = reviews

            for key, value in instances.items():
                self.create_reviews(key, value)

        if isinstance(content, dict):
            reviews = content.pop('reviews')
            content = clean_company_dictionnary(content)

            company_name = content.pop('name')
            company_details.pop('date')
            company_details.pop('number_of_reviews')
            company_name = provided_company_name or company_name
            instance, _ = Company.objects.get_or_create(
                name=company_name,
                defaults=content
            )
            self.create_reviews(instance, reviews)

        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class DownloadFileView(View):
    """Download a csv file containing the data
    for each reviews for a company"""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        queryset = Review.objects.values()
        df = pandas.DataFrame(queryset)
        return create_download_http_response(request, df, file_suffix='reviews')
    

class StartRobotView(View):
    """Starts the robot that gathers the comments
    for a given Google Place or Places"""

    form_class = StartRobotForm

    async def get(self, request, *args, **kwargs):
        return render(request, 'reviews/pages/get_reviews.html')

    async def post(self, request, **kwargs):
        # form = self.form_class(request.POST)
        # if form.is_valid():
        #     url = form.cleaned_data['url']
        #     try:
        #         subprocess.call(['python', '-m', 'google_comments', 'place', url])
        #     except Exception as e:
        #         logging.error(e)
        #         form.add_error(None, 'An error occured when trying to launch the robot')
        # return render(request, 'pages/get_reviews.html', {'form': form})

        async def test_runner():
            import requests
            response = requests.get('http://example.com')
            return response.content

        async def another_thing():
            import requests
            response = requests.get('http://example.com')
            return response.content

        a, b = await asyncio.gather(test_runner(), another_thing())

        return render(request, 'reviews/pages/get_reviews.html', {'a': a, 'b': b})


@require_POST
def caculate_review_sentiment(request, pk, **kwargs):
    company = get_object_or_404(klass=Company, pk=pk)
    reviews = company.review_set.values_list('text', flat=True)
    instance = CalculateSentiment(reviews)
    result = instance.calculate_sentiment()
    add_message(request, messages.SUCCESS, 'Sentiment calculated')
    return redirect(reverse('reviews:list_reviews', args=[pk]))

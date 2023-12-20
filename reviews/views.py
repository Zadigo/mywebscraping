import csv
import json
import subprocess
import asyncio
import logging
from django.db.models.query import QuerySet

import pandas
from asgiref.sync import sync_to_async
from django.shortcuts import render
from django.contrib import messages
from django.contrib.messages import add_message
from django.db import transaction
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.db.models.functions import Length
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, FormView, ListView, View
from mywebscraping.utils import create_filename
from reviews.forms import ReviewsFileUploadForm, SearchForm, StartRobotForm
from reviews.machine_learning.sentiment import CalculateSentiment
from reviews.models import Business, Review
from reviews.utils import (clean_business_dictionnary, clean_reviews,
                           parse_number_of_reviews, parse_rating)


def create_download_http_response(request, dataframe, file_prefix=None, file_suffix=None):
    """Writes the results of a dataframe to an 
    HTTPResponse object"""
    filename = create_filename(prefix=file_prefix, suffix=file_suffix)
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}.csv"'
        }
    )
    response.write(dataframe.to_csv(index=False, encoding='utf-8'))
    return response


class ListBusinesses(ListView):
    model = Business
    queryset = Business.objects.all()
    template_name = 'reviews/list_companies.html'
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


class CompanyView(DetailView):
    model = Business
    queryset = Business.objects.all()
    template_name = 'reviews/reviews.html'
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


class CreateReviewsView(FormView):
    """Upload a file containing Google reviews
    directly using a form"""

    form_class = ReviewsFileUploadForm
    success_url = reverse_lazy('reviews:list_companies')
    template_name = 'reviews/upload.html'

    def create_reviews(self, instance, reviews):
        r1 = clean_reviews(reviews)
        r2 = parse_rating(r1)
        cleaned_reviews = parse_number_of_reviews(r2)

        # for review in cleaned_reviews:
        #     try:
        #         instance.review_set.create(**review)
        #     except:
        #         pass

        instances = []
        for cleaned_review in cleaned_reviews:
            review = Review(
                review_id=f'rev_{get_random_string(length=5)}',
                business=instance,
                **cleaned_review
            )
            instances.append(review)

        objs = Review.objects.bulk_create(instances)

    def form_valid(self, form):
        file = form.cleaned_data['reviews']
        content = json.loads(file.read())

        if isinstance(content, list):
            instances = {}
            for business in content:
                reviews = business.pop('reviews')
                business.pop('date')
                business = clean_business_dictionnary(business)

                business_name = business.pop('name')
                instance, _ = Business.objects.get_or_create(
                    name=business_name,
                    defaults=business
                )
                instances[instance] = reviews
                # self.create_reviews(instance, reviews)

            for key, value in instances.items():
                self.create_reviews(instance, reviews)

        if isinstance(content, dict):
            reviews = content.pop('reviews')
            content = clean_business_dictionnary(content)

            business_name = content.pop('name')
            instance, _ = Business.objects.get_or_create(
                name=business_name,
                defaults=content
            )
            self.create_reviews(instance, reviews)
        return super().form_valid(form)


@method_decorator(never_cache, name='dispatch')
class DownloadFileView(View):
    """Download a csv file containing the data
    for each reviews for a business"""

    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        queryset = Review.objects.values()
        df = pandas.DataFrame(queryset)
        return create_download_http_response(request, df, file_suffix='reviews')
        # filename = get_random_string(length=10)
        # response = HttpResponse(
        #     content_type='text/csv',
        #     headers={
        #         'Content-Disposition': f'attachment; filename="{filename}_reviews.csv"'
        #     }
        # )
        # response.write(df.to_csv(index=False, encoding='utf-8'))
        # return response


@require_POST
def caculate_review_sentiment(request, pk, **kwargs):
    company = get_object_or_404(klass=Business, pk=pk)
    reviews = company.review_set.values_list('text', flat=True)
    instance = CalculateSentiment(reviews)
    result = instance.calculate_sentiment()
    add_message(request, messages.SUCCESS, 'Sentiment calculated')
    return redirect(reverse('reviews:list_reviews', args=[pk]))


class StartRobotView(View):
    """Starts the robot that gathers the comments
    for a given url"""

    form_class = StartRobotForm

    async def get(self, request, *args, **kwargs):
        return render(request, 'pages/get_reviews.html')

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

        return render(request, 'pages/get_reviews.html', {'a': a, 'b': b})

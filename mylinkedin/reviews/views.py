import csv
import json

import pandas
from django.db import transaction
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import DetailView, FormView, ListView, View
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from reviews.forms import ReviewsFileUploadForm
from reviews.models import Business, Review
from reviews.utils import (clean_business_dictionnary, clean_reviews,
                           parse_number_of_reviews, parse_rating)


class ListBusinesses(ListView):
    model = Business
    queryset = Business.objects.all()
    template_name = 'reviews/list_companies.html'
    context_object_name = 'companies'


class ListReviews(ListView):
    model = Review
    queryset = Review.objects.all()
    template_name = 'reviews/list.html'
    context_object_name = 'reviews'


class CompanyView(DetailView):
    model = Business
    queryset = Business.objects.all()
    template_name = 'reviews/reviews.html'
    context_object_name = 'company'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search = self.request.GET.get('search')
        position = self.request.GET.get('position')
        interest = self.request.GET.get('interest')

        company = self.get_object()
        reviews = company.review_set.all()

        # disable_undo_button = True

        # if search is not None:
        #     profiles = profiles.filter(
        #         Q(firstname__icontains=search) |
        #         Q(lastname__icontains=search)
        #     )
        #     disable_undo_button = False

        # if position is not None:
        #     profiles = profiles.filter(position__icontains=position)
        #     disable_undo_button = False

        # if interest is not None:
        #     profiles = profiles.filter(of_interest=True)
        #     disable_undo_button = False

        context['reviews'] = reviews
        # context['searched_search'] = search or ''
        # context['searched_position'] = position or ''
        # context['searched_interest'] = interest
        # print(interest)
        # context['disable_undo_button'] = disable_undo_button
        return context


class CreateReviewsView(FormView):
    form_class = ReviewsFileUploadForm
    success_url = reverse_lazy('reviews:list_companies')
    template_name = 'reviews/upload.html'

    def create_reviews(self, instance, reviews):
        r1 = clean_reviews(reviews)
        r2 = parse_rating(r1)
        cleaned_reviews = parse_number_of_reviews(r2)

        for review in cleaned_reviews:
            try:
                instance.review_set.create(**review)
            except:
                pass

    def form_valid(self, form):
        file = form.cleaned_data['reviews']
        content = json.loads(file.read())

        if isinstance(content, list):
            for business in content:
                reviews = business.pop('reviews')
                business.pop('date')
                business = clean_business_dictionnary(business)

                business_name = business.pop('name')
                instance, _ = Business.objects.get_or_create(
                    name=business_name,
                    defaults=business
                )
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
        filename = get_random_string(length=10)
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}_reviews.csv"'
            }
        )
        response.write(df.to_csv(index=False, encoding='utf-8'))
        return response

from rest_framework.decorators import api_view
from rest_framework.response import Response

from reviews.api.serializers import (BulkReviewForm, BusinessForm,
                                     BusinessSerializer, ReviewForm,
                                     ReviewSerializer)


@api_view(http_method_names=['post'])
def create_review(request, **kwargs):
    """Create a new review in the database"""
    serializer = ReviewForm(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    serialized_review = ReviewSerializer(instance=instance)
    return Response(data=serialized_review.data)


@api_view(http_method_names=['post'])
def create_business(request, **kwargs):
    """Create a new business in the database"""
    serializer = BusinessForm(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    serialized_business = BusinessSerializer(instance=instance)
    return Response(data=serialized_business.data)


@api_view(http_method_names=['post'])
def create_bulk_reviews(request, **kwargs):
    """Create multiple reviews for a given business
    by passing a file or dictionnary that contains
    both business information and reviews"""
    serializer = BulkReviewForm(data=request.data)
    serializer.is_valid(raise_exception=True)
    instance = serializer.save()
    serialized_business = BusinessSerializer(instance=instance)
    return Response(data=serialized_business.data)

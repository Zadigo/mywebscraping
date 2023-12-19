import re

from django.shortcuts import get_object_or_404
from rest_framework import fields
from rest_framework.serializers import Serializer
from reviews.models import Business, Review


class BusinessSerializer(Serializer):
    id = fields.IntegerField(read_only=True)
    business_id = fields.CharField()
    name = fields.CharField()


class ReviewSerializer(Serializer):
    id = fields.IntegerField(read_only=True)
    review_id = fields.CharField()
    text = fields.CharField()
    created_on = fields.DateTimeField()


class BusinessForm(Serializer):
    name = fields.CharField()
    url = fields.URLField()
    feed_url = fields.URLField()
    address = fields.CharField()
    rating = fields.DecimalField(5, decimal_places=2)
    latitude = fields.CharField()
    longitude = fields.CharField()
    number_of_reviews = fields.IntegerField(default=0)
    # additional_information = fields.JSONField()
    telephone = fields.CharField()
    website = fields.URLField()

    def create(self, validated_data):
        business = Business.objects.create(**validated_data)
        return business


class ReviewForm(Serializer):
    business_id = fields.CharField()
    google_review_id = fields.CharField()
    reviewer_name = fields.CharField(required=False)
    reviewer_number_of_reviews = fields.CharField(required=False)
    period = fields.CharField()
    rating = fields.CharField()
    text = fields.CharField()

    def create(self, validated_data):
        business_id = validated_data.pop('business_id')
        rating = validated_data.pop('rating')
        reviewer_number_of_reviews = validated_data.pop(
            'reviewer_number_of_reviews'
        )

        result = re.match(r'^(\d+)', rating)
        if result:
            validated_data['rating'] = result.group(1)

        result = re.match(r'^(\d+)', reviewer_number_of_reviews)
        if result:
            validated_data['reviewer_number_of_reviews'] = result.group(1)

        business = get_object_or_404(Business, business_id=business_id)
        instance = Review.objects.create(**validated_data, business=business)
        return instance


class SimpleReviewForm(Serializer):
    """Allows the creation of a review without
    passing the business_id"""

    google_review_id = fields.CharField()
    reviewer_name = fields.CharField(required=False)
    reviewer_number_of_reviews = fields.CharField(required=False)
    period = fields.CharField()
    rating = fields.CharField()
    text = fields.CharField()


class BulkReviewForm(Serializer):
    """Create reviews by passing both the business
    information and the reviews"""

    name = fields.CharField()
    url = fields.URLField()
    feed_url = fields.URLField()
    address = fields.CharField()
    rating = fields.DecimalField(5, decimal_places=2)
    latitude = fields.CharField()
    longitude = fields.CharField()
    number_of_reviews = fields.IntegerField(default=0)
    # additional_information = fields.JSONField()
    telephone = fields.CharField()
    website = fields.URLField()
    reviews = SimpleReviewForm(many=True)

    def create(self, validated_data):
        reviews = validated_data.pop('reviews')

        instance = Business.objects.create(**validated_data)

        review_objs = []
        for review in reviews:
            result = re.match(r'^(\d+)', review['rating'])
            if result:
                review['rating'] = result.group(1)

            result = re.match(r'^(\d+)', review['reviewer_number_of_reviews'])
            if result:
                review['reviewer_number_of_reviews'] = result.group(1)
            review_objs.append(Review(business=instance, **review))

        reviews = [review.save() for review in review_objs]
        return instance

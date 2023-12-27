import re

from django.shortcuts import get_object_or_404
from rest_framework import fields
from rest_framework.serializers import Serializer

from reviews import utils
from reviews.models import Company, Review


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
    """Form used to create a new review"""

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

        business = get_object_or_404(Company, business_id=business_id)
        instance = Review.objects.create(**validated_data, business=business)
        return instance


class SimpleReviewForm(Serializer):
    """Allows the creation of a review without
    passing the business_id"""

    google_review_id = fields.CharField()
    reviewer_name = fields.CharField(required=False)
    reviewer_number_of_reviews = fields.CharField(
        required=False, 
        allow_null=True
    )
    period = fields.CharField()
    rating = fields.CharField()
    text = fields.CharField(allow_null=True)


class BulkReviewForm(Serializer):
    """Create reviews by passing both the business
    information and its reviews"""

    name = fields.CharField()
    url = fields.URLField()
    feed_url = fields.URLField(allow_null=True)
    address = fields.CharField()
    # rating = fields.DecimalField(5, decimal_places=2)
    rating = fields.CharField()
    latitude = fields.CharField(allow_null=True)
    longitude = fields.CharField(allow_null=True)
    number_of_reviews = fields.IntegerField(default=0)
    additional_information = fields.CharField()
    telephone = fields.CharField()
    website = fields.URLField()
    reviews = SimpleReviewForm(many=True)

    def validate(self, attrs):
        reviews = attrs['reviews']

        r1 = utils.parse_rating(reviews)
        clean_reviews = utils.parse_number_of_reviews(r1)
        attrs['reviews'] = clean_reviews
        
        clean_attrs = utils.clean_company_dictionnary(attrs)

        longitude, latitude = utils.parse_coordinates(attrs['url'])
        clean_attrs['longitude'] = longitude
        clean_attrs['latitude'] = latitude

        return clean_attrs

    def create(self, validated_data):
        reviews = validated_data.pop('reviews')
        instance = Company.objects.create(**validated_data)
        reviews_objs = []
        for review in reviews:
            review['review_id'] = utils.create_id('rev')
            review['company'] = instance
            reviews_objs.append(Review(**review))
        instances = Review.objects.bulk_create(reviews_objs)
        instance.review_set.bulk_create(instances)
        return instance

import re

from django.db.models import Value
from django.utils.crypto import get_random_string
from numpy import isin


def clean_reviews(reviews):
    """Clean the text in the dictionnary for
    each given review"""
    for review in reviews:
        text = review['text']

        if text is None:
            continue

        tokens = text.split(' ')
        tokens = filter(lambda x: x != '', tokens)
        text = ' '.join(tokens)
        text = re.sub('\n', '', text)
        review['text'] = text
        yield review


def parse_rating(reviews):
    """Parse the number value from the incoming
    rating text"""
    for review in reviews:
        value = review['rating']
        if isinstance(value, (int, float)):
            continue

        if value is None:
            continue

        result = re.search('(\d+)', value)
        if result:
            review['rating'] = result.group(1)
        yield review


def parse_number_of_reviews(reviews):
    """Parse the number of reviews left by the
    reviewer in the incoming review number text"""
    for review in reviews:
        value = review['reviewer_number_of_reviews']
        if isinstance(value, (int, float)):
            continue

        if value is None:
            continue

        result = re.search(r'^(\d+)', value)
        if result:
            review['reviewer_number_of_reviews'] = result.group(1)

        result = re.search(r'Local\sGuide\s+\W?\s+(\d+)', value)
        if result:
            review['reviewer_number_of_reviews'] = result.group(1)
        yield review


def clean_company_dictionnary(details):
    """Takes a dictionnary of a values and normalizes
    the text, integers, floats... to Python objects"""
    rating = details['rating']
    if not isinstance(rating, (int, float)):
        result = re.match(r'^(\d\,?\d+)', rating)
        if result:
            value = result.group(1).replace(',', '.')
            details['rating'] = float(value)
    return details


def create_id(prefix, length=10):
    """Creates a random ID value with a prefix"""
    return f'{prefix}_{get_random_string(length=length)}'


def file_upload_helper(instance, name):
    """Upload the review file to the 
    correct directory"""
    name, extension = instance.name
    new_name = get_random_string(length=20)
    return f'reviews/{instance.company_id}/{new_name}.{extension}'


def validate_file_integrity(data):
    expected_columns = set([
        'name', 'url', 'feed_url', 'address', 'rating', 
        'latitude', 'longitude', 'number_of_reviews', 'date', 
        'additional_information', 'telephone', 'website', 'reviews'
    ])

    if isinstance(data, list):
        missing_keys = set()
        for item in data:
            keys = list(item.keys())
            difference = expected_columns.difference(set(keys))
            missing_keys.update(difference)
    
    if isinstance(data, dict):
        keys = list(item.keys())
        difference = expected_columns.difference(set(keys))
        missing_keys.update(difference)

    return missing_keys

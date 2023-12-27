import re

from django.db.models import Value
from django.utils.crypto import get_random_string
from nltk.tokenize import word_tokenize


def clean_reviews_text(reviews):
    """Clean the text in the dictionnary for
    each given review"""
    clean_reviews = []
    for review in reviews:
        text = review['text']

        if text is None:
            clean_reviews.append(review)
            continue

        tokens = word_tokenize(text)
        text = ' '.join(tokens)
        text = re.sub('\n', '', text)
        text = re.sub(';', '', text)
        review['text'] = text
        clean_reviews.append(review)
    return clean_reviews


def parse_rating(reviews):
    """Parse the number value from the incoming
    rating text. This accepts a list of reviews"""
    clean_reviews = []
    for review in reviews:
        value = review['rating']
        if isinstance(value, (int, float)):
            clean_reviews.append(review)
            continue

        if value is None:
            clean_reviews.append(review)
            continue

        result = re.search('(\d+)', value)
        if result:
            review['rating'] = result.group(1)
        clean_reviews.append(review)
    return clean_reviews


def parse_number_of_reviews(reviews):
    """Parse the number of reviews left by the
    reviewer in the incoming review number text.
    This accepts a list of reviews"""
    clean_reviews = []
    for review in reviews:
        value = review['reviewer_number_of_reviews']
        if isinstance(value, (int, float)):
            clean_reviews.append(review)
            continue

        if value is None:
            review['reviewer_number_of_reviews'] = 0
            clean_reviews.append(review)
            continue

        result = re.search(r'^(\d+)', value)
        if result:
            review['reviewer_number_of_reviews'] = result.group(1)

        result = re.search(r'Local\sGuide\s+\W?\s+(\d+)', value)
        if result:
            review['reviewer_number_of_reviews'] = result.group(1)
        clean_reviews.append(review)
    return clean_reviews


def clean_company_dictionnary(details):
    """Takes a dictionnary as in 
    {"name": ..., ..., "reviews": []} and normalizes the 
    text, integers, floats... to Python objects"""
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
    name, extension = name.split('.', maxsplit=1)
    new_name = get_random_string(length=20)
    return f'reviews/{instance.company_id}/{new_name}.{extension}'


def validate_file_reviews(data):
    """Checks that the reviews in the reviews column
    contains the required fields"""
    missing_keys = set()
    expected_review_columns = set([
        'google_review_id', 'text', 'rating',
        'period', 'reviewer_name', 'reviewer_number_of_reviews'
    ])

    def analyze_reviews(reviews):
        for review in reviews:
            difference = expected_review_columns.difference(set(review.keys()))
            missing_keys.update(difference)

    if isinstance(data, list):
        for item in data:
            analyze_reviews(item['reviews'])

    if isinstance(data, dict):
        analyze_reviews(data['reviews'])

    return missing_keys


def validate_file_integrity(data):
    """Checks that the file structure is correct and
    contains all the required fields for upload"""
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


def parse_coordinates(url):
    """From a given url parse the coordinates
    for the given business"""
    if url is None:
        return None, None

    result = re.search(
        r'\/@(?P<latitude>\d+\.\d+)\,(?P<longitude>\d+\.\d+)', url)
    if result:
        items = result.groupdict()
        return items['latitude'], items['longitude']
    return None, None


def create_machine_learning_text(text):
    from nltk.tokenize import word_tokenize
    lower = str(text).lower()
    tokens = word_tokenize(text, language='french')
    return ' '.join(tokens)

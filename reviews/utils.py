import re

from django.db.models import Value


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


def clean_business_dictionnary(details):
    rating = details['rating']
    if not isinstance(rating, (int, float)):
        result = re.match(r'^(\d\,?\d+)', rating)
        if result:
            value = result.group(1).replace(',', '.')
            details['rating'] = float(value)
    return details

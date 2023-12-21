import logging
import pathlib
from functools import cached_property

import nltk
from django.db import models
from django.db.models import Index
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize

from reviews import utils
from reviews.machine_learning.sentiment import calculate_text_sentiment
from reviews.utils import create_id

logger = logging.getLogger('django')

class Company(models.Model):
    """Represents a company"""

    company_id = models.CharField(
        max_length=100,
        unique=True
    )
    name = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )
    feed_url = models.URLField(
        max_length=500,
        blank=True,
        null=True
    )
    address = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    rating = models.PositiveIntegerField(default=0)
    latitude = models.CharField(
        max_length=400,
        blank=True,
        null=True
    )
    longitude = models.CharField(
        max_length=400,
        blank=True,
        null=True
    )
    number_of_reviews = models.PositiveIntegerField(default=0)
    additional_information = models.JSONField(
        help_text=_("Additional information the company"),
        blank=True,
        null=True
    )
    telephone = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )
    website = models.URLField(
        blank=True,
        null=True
    )
    reviews_file = models.FileField(
        upload_to=utils.file_upload_helper,
        blank=True,
        help_text='Optionally save the file containing the reviews'
    )
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on', 'name']
        verbose_name_plural = _('companies')
        indexes = [
            Index(fields=['company_id'])
        ]

    def __str__(self):
        return f'Company: {self.name}'


class Review(models.Model):
    """Represents a single review"""

    review_id = models.CharField(
        max_length=100,
        unique=True
    )
    reviewer_name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    reviewer_number_of_reviews = models.PositiveIntegerField(default=0)
    google_review_id = models.CharField(
        max_length=400,
        help_text=_("The comment ID as referenced by Google")
    )
    company = models.ForeignKey(
        Company,
        models.CASCADE
    )
    period = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    rating = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    text = models.TextField(
        max_length=10000,
        blank=True,
        null=True
    )
    machine_learning_text = models.TextField(
        max_length=10000,
        blank=True,
        null=True
    )
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']
        indexes = [
            Index(fields=['review_id'])
        ]

    def __str__(self):
        return f'Comment: {self.pk}'

    @cached_property
    def sentiment(self):
        return calculate_text_sentiment(self.text)


@receiver(pre_save, sender=Review)
def create_comment_id(instance, **kwargs):
    instance.review_id = create_id('rev')


@receiver(pre_save, sender=Company)
def create_company_id(instance, **kwargs):
    instance.company_id = create_id('comp')


@receiver(post_delete, sender=Company)
def delete_company_reviews_file(instance, **kwargs):
    try:
        path = pathlib.Path(instance.reviews_file.path)
    except Exception:
        # The path is None or Invalid
        return
    else:
        # Make sure that the path exists and
        # that we are dealing with a file to
        # avoid any collateral inconveniences
        if path.exists() and path.is_file():
            parent = path.parent.absolute()
            try:
                parent.rmdir()
            except Exception:
                logger.error(
                    "Could not delete file or "
                    f"directory for {instance.company_id}"
                )
                # If we could not delete the file
                # just continue with the deletion
                # since this is a None critical action
                return


# @receiver(post_save, sender=Review)
# def create_machine_learning_text(instance, created, **kwargs):
#     """Creates a clean text removing stop words, lowering
#     the text for eventual machine learning models"""
#     if created:
#         nltk.download('punkt')
#         tokens = sent_tokenize(instance.text, language='french')
#         lowered_text = ' '.join(token.lower() for token in tokens)

#         nltk.download('stopwords')
#         stop_words = stopwords.words('french')
#         tokens = word_tokenize(lowered_text)
#         clean_text = ' '.join(token for token in tokens if token not in stop_words)
#         instance.machine_learning_text = clean_text
#         instance.save()

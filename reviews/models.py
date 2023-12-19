from django.db import models
from django.db.models import Index
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


class Business(models.Model):
    """Represents a business"""

    business_id = models.CharField(
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
        help_text=_("Additional information the business"),
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
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on', 'name']
        verbose_name_plural = _('businesses')
        indexes = [
            Index(fields=['business_id'])
        ]

    def __str__(self):
        return f'Business: {self.name}'


class Review(models.Model):
    """Represents a business' review"""

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
    business = models.ForeignKey(
        Business,
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
    modified_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']
        indexes = [
            Index(fields=['review_id'])
        ]

    def __str__(self):
        return f'Comment: {self.pk}'


@receiver(pre_save, sender=Review)
def create_comment_id(instance, **kwargs):
    new_id = f'rev_{get_random_string(length=5)}'
    instance.review_id = new_id


@receiver(pre_save, sender=Business)
def create_business_id(instance, **kwargs):
    new_id = f'buis_{get_random_string(length=5)}'
    instance.business_id = new_id

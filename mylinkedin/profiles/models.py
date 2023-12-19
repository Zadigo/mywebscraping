from functools import cached_property
from django.db import models
from django.db.models import UniqueConstraint, Index


class Company(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=True,
        null=True
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    website = models.URLField(
        unique=True,
        blank=True,
        null=True
    )
    linkedin = models.URLField(
        blank=True,
        null=True
    )
    metadata = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    members = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'companies'
        indexes = [
            Index(fields=['name'])
        ]

    def __str__(self):
        return f'Company: {self.name}'


class LinkedinProfile(models.Model):
    company = models.ForeignKey(
        Company,
        models.CASCADE
    )
    firstname = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    lastname = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    url = models.URLField(
        unique=True,
        blank=True,
        null=True
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    of_interest = models.BooleanField(
        default=False,
        help_text='Determines whether the profile is interesting'
    )
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lastname']
        constraints = [
            UniqueConstraint(
                fields=['firstname', 'lastname'],
                name='unique_firstname_lastname'
            )
        ]

    def __str__(self):
        return f'Profile: {self.fullname}'

    @property
    def fullname(self):
        return f'{self.firstname} {self.lastname}'

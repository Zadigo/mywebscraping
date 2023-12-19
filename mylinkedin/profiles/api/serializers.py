from rest_framework import fields
from rest_framework.serializers import Serializer


class CompanySerializer(Serializer):
    name = fields.CharField()
    description = fields.CharField()
    website = fields.URLField()
    linkedin = fields.URLField()
    metadata = fields.CharField()
    members = fields.CharField()


class LinkedinProfileSerializer(Serializer):
    company = CompanySerializer()
    firstname = fields.CharField()
    lastname = fields.CharField()
    url = fields.URLField()
    position = fields.CharField()

from django.core.validators import FileExtensionValidator


def validate_file(name):
    instance = FileExtensionValidator(
        allowed_extensions=['csv', 'json'],
        message='Accepted files a .csv or .json'
    )
    instance(name)

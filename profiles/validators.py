from django.core.validators import FileExtensionValidator


def validate_file(name):
    """Validates that the file is either
    a csv or a json file"""
    instance = FileExtensionValidator(
        allowed_extensions=['csv', 'json'],
        message='Accepted files a .csv or .json'
    )
    instance(name)

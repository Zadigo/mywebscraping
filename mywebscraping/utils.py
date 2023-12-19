from django.utils import timezone
from django.utils.crypto import get_random_string


def create_filename(prefix=None, suffix=None, include_date=True, extension='csv'):
    """Create a new filename which includes five random string, a prefix,
    a suffix, a date and the file extension if required"""
    filename = get_random_string(length=5)

    if prefix is not None:
        filename = f'{prefix}_{filename}'    

    if include_date:
        current_date = timezone.now()
        d = current_date.strftime('%Y-%m-%d %H:%S')
        string_date = d.replace(' ', '-').replace(':', '_')
        filename = filename + f'_{string_date}'
    
    if suffix is not None:
        filename = f'{filename}_{suffix}'

    extension = extension.removeprefix('.')
    return f'{filename}.{extension}'

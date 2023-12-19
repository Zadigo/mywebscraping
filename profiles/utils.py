from profiles.constants import OF_INTEREST
import re


def test_profile_position(value):
    """Checks if the profile's position
    is of interest or not. For instance `director`
    would be an interesting position to check for
    a commercial or marketing team"""
    result = False

    if value is None or value == '' or value == '-':
        return result

    for position in OF_INTEREST:
        if position in value.lower():
            result = True
            break
    return result


def extract_company(value):
    """Extact company name. Example: 
    `(20) Nike : personnes | LinkedIn` would
    become `Nike`"""
    return_value = None
    result = re.match(r'^\(\d+\)\s(.*)\s?\:', str(value))
    if result:
        return_value = result.group(1).strip().upper()
    return return_value or value.upper()

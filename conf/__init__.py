VERSION = "3.9.3"

def get_version(*args, **kwargs):
    # Avoid circular import
    #from django.utils.version import get_version
    #return get_version(*args, **kwargs)
    return VERSION

__version__ = get_version(VERSION)


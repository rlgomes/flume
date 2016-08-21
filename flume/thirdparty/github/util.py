"""
github utilities
"""

from flume.util import IS_PY2

if IS_PY2:
    from urllib import urlencode

else:
    from urllib.parse import urlencode


def github_url(path, **kwargs):
    if len(kwargs) != 0:
        parameters = urlencode(kwargs)
        return 'https://api.github.com/%s?%s' % (path, parameters)

    else:
        return 'https://api.github.com/%s' % path

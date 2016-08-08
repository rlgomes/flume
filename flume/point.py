"""
flume data point class
"""
import json
from datetime import datetime

from flume import moment
from dici import dici


def dmap(dictionary, func):
    result = {}

    for (key, value) in dictionary.items():
        if isinstance(value, dict):
            value = dmap(value, func)

        result[key] = func(value)

    return result

class Point(dici):
    """
    This class represents a data point within the flume pipeline
    """

    def __init__(self, **fields):
        fields = {} if fields is None else fields
        dici.__init__(self, **fields)

        if '__meta__' not in self:
            self['__meta__'] = {'flume_path': ''}

    def hasfield(self, dot_notation):
        """
        returns True if the point has the field expressed with dot notation
        """
        return self.lookup(dot_notation) is not None

    def lookup(self, dot_notation):
        """
        lookup the value of a field specified with the dot notation
        """
        try:
            return self.__getattr__(dot_notation)
        except AttributeError:
            pass
        except KeyError:
            pass

        return None

    def update(self, other):
        """
        update only updates the points fields that aren't within the __meta__ object
        """
        for key in other.keys():
            if key != '__meta__':
                self[key] = other[key]

    def json(self):
        """
        return the JSON serializable representation of this object where all
        of the complex members have been converted into strings
        """
        def handle_dates(value):
            if isinstance(value, datetime):
                return moment.datetime_to_iso8601(value)
            else:
                return value

        result = dmap(self, handle_dates)
        del result['__meta__']
        return result

    def __str__(self):
        return json.dumps(self.json(), sort_keys=True)

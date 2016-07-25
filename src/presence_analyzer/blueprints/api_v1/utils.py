# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""
import calendar
import csv
import logging

from datetime import datetime
from functools import wraps
from json import dumps
from lxml import etree
from flask import Response

from presence_analyzer.main import app
from presence_analyzer.blueprints.api_v1.exceptions import UserNotFoundError
from presence_analyzer.cache import MemoryCache

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

cache_backend = MemoryCache()  # pylint: disable=invalid-name


def cache(time):
    """
    Cache decorator used to cache any function using CACHE_BACKEND.
    :param time: caching time (seconds)
    :return: result of function
    """
    def _cache(function):
        """
        The real decorator.
        """
        def wrapper(*args, **kwargs):
            """
            Wrapper function.
            """
            return cache_backend.get_or_set(function, time, *args, **kwargs)
        return wrapper
    return _cache


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    :param function: View function
    :return: Response object with mimetype set to json and result of wrapped
             function dumped to JSON
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        This docstring will be overridden by @wraps decorator.
        """
        return Response(
            dumps(function(*args, **kwargs)),
            mimetype='application/json'
        )
    return inner


@cache(60)
def get_personal_data():
    """
    Extracts personal data (name, avatar url) from XML file and groups it by
    user_id
    :return: Dict structured like that:
    data = {
        'user_id': {
            'name': 'Jacek S.',
            'avatar_url': 'https://intranet.stxnext.pl/api/images/users/496'
        }
        ...
    """
    result = {}
    tree = etree.parse(  # pylint: disable=maybe-no-member
        app.config['USER_DATA_XML']
    )
    server_data = tree.xpath('//server')[0]
    host = server_data.findtext('host')
    protocol = server_data.findtext('protocol')
    for user in tree.xpath('//users/user'):
        user_id = int(user.get('id'))
        name = user.findtext('name')
        avatar_path = user.findtext('avatar')
        avatar_url = '{protocol}://{host}{avatar_path}'.format(
            protocol=protocol,
            host=host,
            avatar_path=avatar_path,
        )
        result[user_id] = {
            'name': name,
            'avatar_url': avatar_url,
        }
    return result


def get_user_personal_data(user_id):
    """
    Gets personal data (name, avatar url) for specified user.
    :param user_id: Integer
    :return: Dict structured like that:
    data = {
        'name': 'Jacek S.',
        'avatar_url': 'https://intranet.stxnext.pl/api/images/users/496'
    }
    """
    data = get_personal_data()
    return data.get(user_id)


@cache(60)
def get_presence_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            }
        }
    }

    :return: Dict structured as above
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
                data.setdefault(user_id, {})[date] = {
                    'start': start,
                    'end': end
                }
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

    return data


def get_user_presence_data(user_id):
    """
    Returns user-specific data.
    :param user_id: Integer
    :return: Dict with datetime object as key, with dict as value containing
            start and end of presence as datetime.
    """
    data = get_presence_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        raise UserNotFoundError('User not found')
    return data[user_id]


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    :param items: Dict with datetime object as key, every value is dict
                  containing start and end of presence as datetime
    :return: List of lists, one list per day of week, containing all presence
             entries as int (seconds)
    """
    result = [[], [], [], [], [], [], []]  # one list for every day in week
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_start_end_by_weekday(items):
    """
    Groups start and end entries per weekday.
    :param items: Dict with datetime object as key, every value is dict
                  containing start and end of presence as datetime
    :return: Dict with 7 keys (0-7), one dict per day of week, containing all
             start and end entries as int (seconds).
    """
    result = {k: {'start': [], 'end': []} for k in xrange(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()]['start'].append(seconds_since_midnight(start))
        result[date.weekday()]['end'].append(seconds_since_midnight(end))
    return result


def count_average_start_end_time(items):
    """
    Counts average start and end time as seconds from midnight for dict of day
    dictionaries ({'start': [123, 345], 'end': [867, 998]})
    :param items: dict of dictionaries as written above
    :return: list of 7 lists, every list contains 3 elements:
    - abbreviated name of week day,
    - average start time,
    - average end time.
    """
    result = []
    for idx, day in items.iteritems():
        result.append(
            [
                calendar.day_abbr[idx],
                mean(day['start']),
                mean(day['end']),
            ]
        )
    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    :param time: Time object
    :return: Integer (seconds)
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates interval in seconds between two datetime.time objects.
    :param start: datetime.time object
    :param end: datetime.time object
    :return: Integer
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    :param items: List of integers
    :return: Float, arithmetic mean
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0

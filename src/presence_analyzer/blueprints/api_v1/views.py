# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging

from flask import Blueprint
from flask import jsonify as jsonify_func

from presence_analyzer.blueprints.api_v1.exceptions import UserNotFoundError
from presence_analyzer.blueprints.api_v1.utils import (
    jsonify, get_data, mean, group_by_weekday,
    group_start_end_by_weekday, count_average_start_end_time, get_user_data
)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

api_v1 = Blueprint('api_v1', __name__)  # pylint: disable=C0103


@api_v1.errorhandler(UserNotFoundError)
def user_not_found(error):
    """
    Returns 404 when UserNotFoundError exception is thrown.
    """
    return jsonify_func(dict(success=False, message=error.message)), 404


@api_v1.route('/users', methods=['GET'])
@jsonify
def api_users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@api_v1.route('/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def api_mean_time_weekday_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    user_data = get_user_data(user_id)
    weekdays = group_by_weekday(user_data)
    result = [
        (calendar.day_abbr[weekday], mean(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    return result


@api_v1.route('/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def api_presence_weekday_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    user_data = get_user_data(user_id)
    weekdays = group_by_weekday(user_data)
    result = [
        (calendar.day_abbr[weekday], sum(intervals))
        for weekday, intervals in enumerate(weekdays)
    ]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@api_v1.route('/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def api_presence_start_end_view(user_id):
    """
    Returns average start and end of work for user for every weekday
    """
    user_data = get_user_data(user_id)
    weekdays = group_start_end_by_weekday(user_data)
    average_start_end = count_average_start_end_time(weekdays)
    return average_start_end

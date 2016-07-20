# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
import logging

from flask import redirect
from flask import jsonify as jsonify_func

from presence_analyzer.exceptions import UserNotFoundError
from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify, get_data, mean, group_by_weekday,
    group_start_end_by_weekday, count_average_start_end_time, get_user_data
)

log = logging.getLogger(__name__)  # pylint: disable=invalid-name


@app.errorhandler(UserNotFoundError)
def user_not_found(error):
    """
    Returns 404 when UserNotFoundError exception is thrown.
    """
    return jsonify_func(dict(success=False, message=error.message)), 404


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect('/static/presence_weekday.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    return [
        {'user_id': i, 'name': 'User {0}'.format(str(i))}
        for i in data.keys()
    ]


@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_view(user_id):
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


@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_view(user_id):
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


@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_view(user_id):
    """
    Returns average start and end of work for user for every weekday
    """
    user_data = get_user_data(user_id)
    weekdays = group_start_end_by_weekday(user_data)
    average_start_end = count_average_start_end_time(weekdays)
    return average_start_end

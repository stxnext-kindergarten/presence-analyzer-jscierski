# -*- coding: utf-8 -*-
"""
Defines views.
"""

from flask import Blueprint, redirect, render_template, url_for

website = Blueprint(  # pylint: disable=C0103
    'website',
    __name__,
    template_folder='templates',
)


@website.route('/')
def mainpage():
    """
    Redirects to mean time per weekday page.
    """
    return redirect(url_for('website.presence_weekday_view'))


@website.route('/mean_time_weekday')
def mean_time_weekday_view():
    """
    Renders mean_time_weekday template.
    """
    return render_template('mean_time_weekday.html')


@website.route('/presence_start_end')
def presence_start_end_view():
    """
    Renders presence_start_end template.
    """
    return render_template('presence_start_end.html')


@website.route('/presence_weekday')
def presence_weekday_view():
    """
    Renders presence_weekday template.
    """
    return render_template('presence_weekday.html')

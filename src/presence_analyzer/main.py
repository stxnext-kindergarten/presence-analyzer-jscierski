# -*- coding: utf-8 -*-
"""
Flask app initialization.
"""
import os.path
from flask import Flask


MAIN_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'sample_data.csv'
)

USER_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'users.xml'
)
USERS_XML_URL = 'http://sargo.bolt.stxnext.pl/users.xml'

app = Flask(__name__)  # pylint: disable=invalid-name

app.config.update(
    DEBUG=True,
    DATA_CSV=MAIN_DATA_CSV,
    USER_DATA_XML=USER_DATA_XML,
    USERS_XML_URL=USERS_XML_URL,
)

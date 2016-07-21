# -*- coding: utf-8 -*-
"""
Scripts used by cronjobs.
"""
import requests

from presence_analyzer.main import app


def download_xml():
    """
    Script for downloading XML file with users data. Used by cronjob.
    Gets config from Flask app.
    """
    xml_url = app.config['USERS_XML_URL']
    xml_filename = app.config['USER_DATA_XML']
    resp = requests.get(xml_url)
    if resp.status_code == 200:
        with open(xml_filename, 'w') as xml:
            for chunk in resp.iter_content():
                xml.write(chunk)

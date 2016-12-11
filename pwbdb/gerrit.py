# -*- coding: utf-8  -*-

import json

import requests


GERRIT_REST_API_ROOT = 'https://gerrit.wikimedia.org/r/'


def get_changes():
    response = requests.get(
        '{}changes/?q=status:open+project:pywikibot/core+branch:master'.format(
            GERRIT_REST_API_ROOT))

    return json.loads(response.text[4:])

# -*- coding: utf-8  -*-

import json
from os import path

import requests
from git import Repo


GERRIT_REST_API_ROOT = 'https://gerrit.wikimedia.org/r/'


def get_changes():
    response = requests.get(
        '{}changes/?q=status:open+project:pywikibot/core+branch:master&o=ALL_REVISIONS'.format(
            GERRIT_REST_API_ROOT))

    return json.loads(response.text[4:])


def fetch_branch(change):
    repo = Repo.init(path.join(path.dirname(__file__), '..', 'pywikibot-core'))
    gerrit_remote = repo.remotes['gerrit']

    revisions = change['revisions']
    newest_revision = max(revisions.values(), key=lambda v: v['_number'])
    remote_ref = newest_revision['ref']

    local_ref = 'gerrit-{}-{}'.format(
        change['_number'], newest_revision['_number'])

    if local_ref not in repo.branches:
        gerrit_remote.fetch('{}:{}'.format(remote_ref, local_ref))
    return repo.branches[local_ref]

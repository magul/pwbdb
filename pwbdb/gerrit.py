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


def newest_revision_number(change):
    revisions = change['revisions']
    newest_revision = max(revisions.values(), key=lambda v: v['_number'])
    return newest_revision['_number']


def fetch_branch(change):
    repo = Repo.init(path.join(path.dirname(__file__), '..', 'pywikibot-core'))
    gerrit_remote = repo.remotes['gerrit']

    revisions = change['revisions']
    newest_revision = max(revisions.values(), key=lambda v: v['_number'])
    remote_ref = newest_revision['ref']

    local_ref = 'gerrit-{}-{}'.format(
        change['_number'], newest_revision_number(change))

    if local_ref not in repo.branches:
        gerrit_remote.fetch('{}:{}'.format(remote_ref, local_ref))
    return repo.branches[local_ref]


def get_unanswered_changes():
    response = requests.get(
        '{}changes/?q=status:open+project:pywikibot/core+branch:master&o=MESSAGES'.format(
            GERRIT_REST_API_ROOT))
    changes = json.loads(response.text[4:])
    for ch in changes:
        message_counter, last_comment_author = -1, 75
        while last_comment_author == 75:
            last_comment_author = ch['messages'][message_counter]['author']['_account_id']
            message_counter += 1

        if last_comment_author != 1000:
            print('https://gerrit.wikimedia.org/r/#/c/{}/'.format(ch['_number']))

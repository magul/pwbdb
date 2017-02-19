# -*- coding: utf-8  -*-

import json
from os import path

import requests
from git import Repo
from requests.auth import HTTPDigestAuth

from pwbdb import appveyor, travis


GERRIT_REST_API_ROOT = 'https://gerrit.wikimedia.org/r/'
GERRIT_AUTH_REST_API_ROOT = '{}a/'.format(GERRIT_REST_API_ROOT)


def get_changes():
    response = requests.get(
        '{}changes/?q=status:open+project:pywikibot/core+branch:master&o=ALL_REVISIONS'.format(
            GERRIT_REST_API_ROOT))

    return json.loads(response.text[4:])


def newest_revision_number(change):
    revisions = change['revisions']
    newest_revision = max(revisions.values(), key=lambda v: v['_number'])
    return newest_revision['_number']


def fetch_master():
    repo = Repo.init(path.join(path.dirname(__file__), '..', 'pywikibot-core'), bare=True)
    gerrit_remote = repo.remotes['gerrit']
    gerrit_remote.fetch('master:master')
    return repo.branches['master']


def fetch_branch(change):
    repo = Repo.init(path.join(path.dirname(__file__), '..', 'pywikibot-core'), bare=True)
    gerrit_remote = repo.remotes['gerrit']

    revisions = change['revisions']
    newest_revision = max(revisions.values(), key=lambda v: v['_number'])
    remote_ref = newest_revision['ref']

    local_ref = 'gerrit-{}-{}'.format(
        change['_number'], newest_revision_number(change))

    if local_ref not in repo.branches:
        gerrit_remote.fetch('{}:{}'.format(remote_ref, local_ref))
    return repo.branches[local_ref]


def comment_on_newest_revision(change, message, creds):
    newest_revision = newest_revision_number(change)
    response = requests.post(
        '{}changes/{}/revisions/{}/review'.format(
            GERRIT_AUTH_REST_API_ROOT,
            change['_number'],
            newest_revision),
        json={'message': message},
        auth=HTTPDigestAuth(creds.GERRIT_HTTP_USER, creds.GERRIT_HTTP_PASS))
    return json.loads(response.text[4:])


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


def post_comment_about_CI(change, pr, creds=None):
    if creds is None:
        creds = {}

    message = """
Test suite has been ran on Github-defined CI environments.

For more details see:
 * Github PR: {github_pr}
 * Travis reference build: {travis_base}
 * Travis change build: {travis_pr}
 * AppVeyor reference build: {appveyor_base}
 * AppVeyor changes build: {appveyor_pr}
    """

    message_kwargs = {
        'github_pr': pr.html_url,
        'travis_base': travis.get_build_url(pr.base, creds=creds),
        'travis_pr': travis.get_build_url(pr.head, build_type='pr', creds=creds),
        'appveyor_base': appveyor.get_build_url(pr.base, creds=creds),
        'appveyor_pr': appveyor.get_build_url(pr.head, build_type='pr', creds=creds)
    }

    if all(message_kwargs.values()):
        if int(pr.title.split('-')[-1]) == newest_revision_number(change):
            all_messages = json.loads(requests.get('{}changes/?q={}&o=MESSAGES'.format(
                GERRIT_REST_API_ROOT, change['_number'])).text[4:])[0]['messages']
            newest_revision_messages = [
                m for m in all_messages
                if m['_revision_number'] == newest_revision_number(change)
            ]
            has_comment_already = any([
                m for m in newest_revision_messages
                if (m['author']['_account_id'] == 1000 and 'https://travis-ci' in m['message'])
            ])
            if not has_comment_already:
                comment_on_newest_revision(change, message.format(**message_kwargs), creds=creds)

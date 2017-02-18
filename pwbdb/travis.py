# -*- coding: utf-8  -*-

import gzip
import os
from os import path

import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
from travispy import TravisPy

from .github import GITHUB_REPO, UPSTREAM_GITHUB_REPO

travis_repo = 'wikimedia/pywikibot-core'
logs_dir = path.join(path.dirname(__file__), '..', 'travis-logs')


def get_build_url(commit, build_type='push', creds=None, upstream_repo=False):
    if creds is None:
        creds = {}

    statuses = requests.get(
        'https://api.github.com/repos/{}/statuses/{}'.format(
            UPSTREAM_GITHUB_REPO if upstream_repo else GITHUB_REPO,
            commit.sha),
        auth=HTTPBasicAuth(creds.GITHUB_USER, creds.GITHUB_PASS)).json()
    pr_statuses = [
        s for s in statuses
        if s['context'] == 'continuous-integration/travis-ci/{}'.format(build_type)]

    if len(pr_statuses) == 0:
        if upstream_repo:
            return None
        return get_build_url(commit, build_type, creds, upstream_repo=True)

    return max(pr_statuses, key=lambda s: s['created_at'])['target_url']


def get_travis_logs():
    t = TravisPy()
    r = t.repo(travis_repo)
    bs = t.builds(repository_id=r.id)
    while int(bs[-1].number) > 1:
        bs.extend(t.builds(repository_id=r.id, after_number=bs[-1].number))

    for b in tqdm(bs):
        bdir = path.join(logs_dir, str(b.id))
        if not path.exists(bdir):
            os.mkdir(bdir)
            for jid in b.job_ids:
                log = requests.get(
                    'https://api.travis-ci.org/'
                    'jobs/{}/log.txt?deansi=true'.format(jid))
                logfile = path.join(bdir, '{}.log.gz'.format(jid))
                with gzip.open(logfile, 'wb') as f:
                    f.write(bytearray(log.text, 'utf-8'))

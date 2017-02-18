# -*- coding: utf-8  -*-

import requests
from requests.auth import HTTPBasicAuth

from .github import GITHUB_REPO, UPSTREAM_GITHUB_REPO


def get_build_url(commit, build_type='branch', creds=None, upstream_repo=False):
    if creds is None:
        creds = {}

    statuses = requests.get(
        'https://api.github.com/repos/{}/statuses/{}'.format(
            UPSTREAM_GITHUB_REPO if upstream_repo else GITHUB_REPO,
            commit.sha),
        auth=HTTPBasicAuth(creds.GITHUB_USER, creds.GITHUB_PASS)).json()

    pr_statuses = [
        s for s in statuses
        if s['context'] == 'continuous-integration/appveyor/{}'.format(build_type)]

    if len(pr_statuses) == 0:
        if upstream_repo:
            return None
        return get_build_url(commit, build_type, creds, upstream_repo=True)

    return max(pr_statuses, key=lambda s: s['created_at'])['target_url']

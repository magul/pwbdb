# -*- coding: utf-8  -*-

import requests
from travispy import TravisPy


def get_travis_build(github_pr):
    statuses = requests.get(github_pr.raw_data['statuses_url']).json()
    pr_statuses = [
        s for s in statuses
        if s['context'] == 'continuous-integration/travis-ci/pr']

    if len(pr_statuses) == 0:
        return None

    pr_status = max(pr_statuses, key=lambda s: s['created_at'])
    travis = TravisPy()
    build = travis.build(pr_status['target_url'].split('/')[-1])

    if build.state in ('creted', 'started'):
        return None

    return build


def get_travis_jobs(build):
    travis = TravisPy()
    return [travis.job(job_id) for job_id in build.job_ids]

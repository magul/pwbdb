# -*- coding: utf-8  -*-

import gzip
import os
from os import path

import requests
from tqdm import tqdm
from travispy import TravisPy

travis_repo = 'wikimedia/pywikibot-core'
logs_dir = path.join(path.dirname(__file__), '..', 'travis-logs')


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

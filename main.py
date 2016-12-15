# -*- coding: utf-8  -*-

import gzip
import os
from os import path

from tqdm import tqdm

import credentials
from pwbdb import gerrit, github, travis


def create_github_pr_from_gerrit():
    for change in tqdm(gerrit.get_changes()):
        local_branch = gerrit.fetch_branch(change)
        github_ref = github.push_branch(local_branch)
        github.open_pull_request(github_ref, creds=credentials)


def test_downloaded_travis_builds(test_func):
    logs_dir = path.join(path.dirname(__file__), 'travis-logs')
    for b in os.listdir(logs_dir):
        bdir = path.join(logs_dir, b)
        for j in os.listdir(bdir):
            jfile = path.join(bdir, j)
            with gzip.open(jfile) as f:
                if test_func(str(f.read())):
                    print('{}/{}'.format(b, j))


def get_travis_logs():
    travis.get_travis_logs()


if __name__ == '__main__':
    get_travis_logs()

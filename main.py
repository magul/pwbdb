# -*- coding: utf-8  -*-

from tqdm import tqdm

import credentials
from pwbdb import gerrit, github, travis

if __name__ == '__main__':
    for change in tqdm(gerrit.get_changes()):
        local_branch = gerrit.fetch_branch(change)
        github_ref = github.push_branch(local_branch)
        github_pr = github.open_pull_request(github_ref, creds=credentials)
        travis_build = travis.get_travis_build(github_pr)

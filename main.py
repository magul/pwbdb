# -*- coding: utf-8  -*-

import credentials
from pwbdb import gerrit, github

if __name__ == '__main__':
    for change in gerrit.get_changes():
        print(change['_number'])
        local_branch = gerrit.fetch_branch(change)
        github_ref = github.push_branch(local_branch)
        github.open_pull_request(github_ref, creds=credentials)

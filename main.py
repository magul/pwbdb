# -*- coding: utf-8  -*-

from pwbdb import gerrit, github

if __name__ == '__main__':
    for change in gerrit.get_changes():
        local_branch = gerrit.fetch_branch(change)
        github.push_branch(local_branch)

# -*- coding: utf-8  -*-

from github import Github


GITHUB_REPO = 'magul/pywikibot-core'


def push_branch(local_branch):
    name = local_branch.name
    repo = local_branch.repo
    github = repo.remotes['github']

    return github.push(name)[0].remote_ref


def open_pull_request(branch, creds=None):
    if creds is None:
        creds = {}

    github = Github(creds.GITHUB_USER, creds.GITHUB_PASS)

    name = branch.remote_head

    repo = github.get_repo(GITHUB_REPO)

    pull_requests = [p for p in repo.get_pulls() if p.head.ref == name]
    if len(pull_requests) > 0:
        return pull_requests[0]
    return repo.create_pull(title=name, body='', head=name, base='master')

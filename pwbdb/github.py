# -*- coding: utf-8  -*-

from github import Github


UPSTREAM_GITHUB_REPO = 'wikimedia/pywikibot-core'
GITHUB_REPO = 'magul/pywikibot-core'

_pull_requests = []


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

    global _pull_requests
    if len(_pull_requests) == 0:
        _pull_requests = [p for p in repo.get_pulls()]
    pull_requests = [p for p in _pull_requests if p.head.ref == name]
    if len(pull_requests) > 0:
        return pull_requests[0]
    return repo.create_pull(title=name, body='', head=name, base='master')


def get_branches(creds=None):
    if creds is None:
        creds = {}

    github = Github(creds.GITHUB_USER, creds.GITHUB_PASS)

    repo = github.get_repo(GITHUB_REPO)
    return repo.get_branches()

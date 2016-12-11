# -*- coding: utf-8  -*-


def push_branch(local_branch):
    name = local_branch.name
    repo = local_branch.repo
    github = repo.remotes['github']

    if 'github/{}'.format(name) not in github.fetch():
        github.push(name)

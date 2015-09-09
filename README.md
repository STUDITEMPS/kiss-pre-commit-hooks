This repo contains git-partial-flake8 to check flake8 only for changed files.

This based on http://pre-commit.com/ by yelp


# Install
To register this hook to "Yelp's pre-commit" use

Add this file to your project:

    .pre-commit-config.yaml

with this content:

    -   repo: https://github.com/STUDITEMPS/kiss-pre-commit-hooks.git
        sha: 1c9cbe9bbc854f091ed31d2bd1b5bdacf0dcd0a6
        hooks:
        -   id: partial-flake8

install pre-commit to your project

    pre-commit install && pre-commit autoupdate
    

# Changelog
* Initial import
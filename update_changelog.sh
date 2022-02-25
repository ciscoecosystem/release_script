#!/bin/bash

# 1. Update CHANGELOG.rst
cd $1/..
source env/bin/activate
cd $1
antsibull-changelog release -v

# 2. Update galaxy.yml

# 3. Push updated files to repo
git add -u
git status
git commit -m 'Update change log & galaxy.yml'
git clean -f -d
# FIXED: make a PR for this commit

# 4. Create a releasing PR and wait for it merged
gh pr create


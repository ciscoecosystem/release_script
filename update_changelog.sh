#!/bin/bash

# 1. Update CHANGELOG.rst
cd $1/..
source env/bin/activate
cd $1

antsibull-changelog release -v

# 2. Push updated files to repo
cat ./changelogs/changelog.yaml
git add -u
git status
git commit -m 'Update change log & galaxy.yml'
# push branch to the remote repo where you want to create the PR
git push -f $3
git clean -f -d

# 3. Create a releasing PR and wait for it merged
# close the pr with the same name
gh pr close $2
gh pr create --title $2 --body ""


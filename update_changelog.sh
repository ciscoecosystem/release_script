#!/bin/bash

# 1. Update CHANGELOG.rst
# cd $1/..
# source env/bin/activate
cd $1
cat ./changelogs/changelog.yaml
antsibull-changelog release -v

# 2. Push updated files to repo
git config user.email "dcn-ecosystem@cisco.com"
git config user.name "dcn-ecosystem"
# git push --set-upstream origin $2
cat ./changelogs/changelog.yaml
git add -u
git status
git commit -m "[ignore] Update Changelog for new release (v$3)"
# push branch to the remote repo where you want to create the PR
git push -f origin $2
git clean -f -d

# 3. Create a releasing PR and wait for it merged
# close the pr with the same name
gh pr close $2
gh pr create --title $2 --body ""


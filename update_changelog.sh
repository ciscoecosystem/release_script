#!/bin/bash

# 1. Update CHANGELOG.rst
cd $1/..
source env/bin/activate
cd $1
antsibull-changelog release -v

# 2. Push updated files to repo
git add -u
git status
git commit -m 'Update change log & galaxy.yml'
git clean -f -d
# TODO: make a PR for this commit

# 3. Build collection
cd $1
rm cisco-$2-*
ansible-galaxy collection build --force
ansible-galaxy collection install cisco-$2-* --force


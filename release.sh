#!/bin/bash
# This is script to get latest version of collection and install antsibull

# cd to directory of the collection
# directory is absolute path
cd $1
# 1. Create a new branch release_{target_version} and get latest version
git checkout master
git fetch $2 master
git reset --hard origin/master
git branch -D $3
git checkout -b $3

# 2. Install and activate virtual python environment
cd ..
python3 -m pip install --user virtualenv
python3 -m venv env
source env/bin/activate

# 3. Install antsibull
pip install antsibull-changelog

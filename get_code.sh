#!/bin/bash
# 1. Get latest version after releasing PR merged
cd $1
git checkout master
git fetch $4 master
git reset --hard origin/master
git branch -D $3
git checkout -b $3

# 2. Build collection
cd $1
rm cisco-$2-*
ansible-galaxy collection build --force
ansible-galaxy collection install cisco-$2-* --force
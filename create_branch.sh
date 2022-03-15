#!/bin/bash
# This script creates a release_pr branch

# cd to directory of the collection
# directory is absolute path
cd $1
# 1. Create a new branch release_pr and get latest version
git remote -v
git checkout -b $3
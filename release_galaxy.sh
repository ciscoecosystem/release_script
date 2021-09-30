#!/bin/bash

cd $1

#gh auth login
gh release delete v$3
gh release create v$3 -F ./release_content.txt -t v$3 ./cisco-$2-$3.tar.gz
# release_script
##### This release_seript is used to do the ansible release automatically
#### How to use this script
##### 1. Define configuration file 'arguments.txt'. 
In 'arguments.txt', we give these arguments:
repo_url : Github API to get repo info. For example: https://api.github.com/repos/CiscoDevNet/ansible-mso
target_version: The version we want to release. For example: 1.0.0
collection_name: The name of ansible collection. For example: mso
directory: Local directory where we develop our ansible collection. For example: /Users/yourName/ansible-mso
remote_branch: Remote name which represents the official collection repo. Use git remote -v to check which one we want to use. For example: origin
##### 2. Run script with configuration file
Use command below:
python3 script.py arguments.txt

##### 3. Get an updated changelog.yaml file from step 1, and then modify this changelog.yaml file manually if necessary.
In this updated changelog.yaml, we put all commits under 'untagged' label into correct labels ('bugfixes', 'minor_changes', 'major_changes') and remove those unnecessary commits along with 'untagged' label.

##### 4. New version released 
#### How to write proper commit message in order to use this script
For each commit, we add commit message with proper prefix 'bugfixes: ', 'minor_changes: ', 'major_changes: '
For example: git commit -m 'bugfixes: CommitMessageWeWrite'
Note: There must be a space between colon and message
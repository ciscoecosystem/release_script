# script to collect commit message
#!/usr/bin/python
# from simple_term_menu import TerminalMenu
import requests
# import sys
import yaml
# import configparser
import datetime
import os
import re


def parse_commit_msg(commit_str):
    # return a list [commit_type, commit_msg]
    commit_line=re.sub(r'''['\n]+''', ' ', commit_str)
    commit_match = re.match(r'''^['\s]*\[?([\w\s-]+)\s*\]?:?\s*(.+)['\s]*$''', commit_line)
    if commit_match:
        commit_groups = commit_match.groups()
        commit_type = commit_groups[0]
        commit_msg = commit_groups[1]
    else:
        commit_type = "trivial"
        commit_msg = commit_line
    return commit_type, commit_msg

def parse_commit_type(commit_type):
    if re.search("bug", commit_type.lower()):
        res_type = "bugfixes"
    elif re.search("major", commit_type.lower()):
        res_type = "major_changes"
    elif re.search("minor", commit_type.lower()):
        res_type = "minor_changes"
    elif re.search("ignore", commit_type.lower()):
        res_type = "ignore_changes"
    else:
        res_type = "trivial"
    return res_type

def parse_commit_content(commit_msg):
    res_msg = commit_msg
    if re.match(r'''^[a-z]''', commit_msg):
        res_msg = commit_msg[0].upper() + commit_msg[1:]
    return res_msg


# config = configparser.ConfigParser()
# # add condition
# config.read(sys.argv[1])

# Use var get from github action env var
# repo_url replace by env var
# repo_url = config['settings']['repo_url']
repo = os.getenv('GITHUB_REPOSITORY')
repo_url = "https://api.github.com/repos/" + repo
github_token = os.getenv('GITHUB_TOKEN')
pr_name = "release_pr"

# parse var repo to get the collection name
# collection = config['settings']['collection_name']
# collection_name = 'ansible-' + collection
collection_name = repo.split("/")[1]

# target version can be proposed while generating changlog file
# target_version = config['settings']['target_version']

latest = requests.get('{0}/releases/latest'.format(repo_url))
latest_version = latest.json().get('tag_name')
print("The latest release: " + latest_version)

url = '{0}/compare/{1}...master'.format(repo_url, latest_version)

r = requests.get(url)
result = r.json()
commits = result.get('commits')

print("The repo is " + repo)
print("The repo_url is " + repo_url)
print("The compare url is " + url)

bug = []
minor = []
major = []
trivial = []

# cd to directory of the collection
# directory is an absolute path
# collection directory in github action ubuntu
# directory = config['settings']['directory']
directory = "./collection"
script_dir = "./release_script"

# remote branch is defined in github action as origin
# remote_branch = config['settings']['remote_branch']
remote_branch = "origin"
change_log_path = '{0}/changelogs/changelog.yaml'.format(directory)

# options = ["Update changelog and create a releasing PR", "Build collection and release"]
# terminal_menu = TerminalMenu(options)
# menu_entry_index = terminal_menu.show()
# if menu_entry_index == 0:
    # 1. Create a new branch release_{target_version} and get latest version
    # os.system("cd {0} && git checkout master && git branch -D release_{1} && git checkout -b release_{2}".format(directory, target_version, target_version))
os.system("chmod +x {0}/create_branch.sh && {1}/create_branch.sh {2} {3} {4}".format(script_dir, script_dir, directory, remote_branch, pr_name))

# 2. Update changelog.yml
# put all commit msg without prefix into trivial list
for commit in commits:
    # detect whether the commit msg is multiple line, if so, split into different commit msg
    # rm single quote
    # use regex to match
    commit_message = commit.get('commit').get('message')
    print("Commit Message: " + commit_message)
    commit_type, commit_msg = parse_commit_msg(commit_message)
    parsed_commit_type = parse_commit_type(commit_type)
    parsed_commit_content = parse_commit_content(commit_msg)

    if parsed_commit_type == 'bugfixes':
        bug.append(parsed_commit_content)
    elif parsed_commit_type == 'minor_changes':
        minor.append(parsed_commit_content)
    elif parsed_commit_type == 'major_changes':
        major.append(parsed_commit_content)
    elif parsed_commit_type == 'ignore_changes':
        pass
    else:
        trivial.append(parsed_commit_content)

print("The trivial commits are: " + str(trivial))
print("The bug commits are: " + str(bug))
print("The minor commits are: " + str(minor))
print("The major commits are: " + str(major))

release_date = datetime.date.today()

# propose the version number target version
latest_version_split = latest_version[1:].split(".")
if major:
    latest_version_split[0] = str(int(latest_version_split[0])+1)
    latest_version_split[1] = "0"
    latest_version_split[2] = "0"
elif minor:
    latest_version_split[1] = str(int(latest_version_split[1])+1)
    latest_version_split[2] = "0"
else:
    latest_version_split[2] = str(int(latest_version_split[2])+1)
target_version = ".".join(latest_version_split)

change_log = dict(
    changes = dict(
        release_summary = 'Release v{0} of the ``{1}`` collection on {2}.\nThis changelog describes all changes made to the modules and plugins included in this collection since {3}.\n'.format(target_version, collection_name, release_date, latest_version)
    ),
    release_date = str(release_date)
)

if len(bug) > 0:
    change_log['changes']['bugfixes'] = bug
if len(minor) > 0:
    change_log['changes']['minor_changes'] = minor
if len(major) > 0:
    change_log['changes']['major_changes'] = major
if len(trivial):
    change_log['changes']['trivial'] = trivial

print("Changelog: " + str(change_log))

with open(change_log_path) as f:
    dataMap = yaml.safe_load(f)
    dataMap['releases'][target_version] = change_log
with open(change_log_path, 'w') as f:
    yaml.dump(dataMap, f)

# edit changelog.yaml as we want
# os.system("vim {0}".format(change_log_path))

# 3. Update galaxy.yml
galaxy_path = '{0}/galaxy.yml'.format(directory)

with open(galaxy_path, 'r') as f:
    data = f.read().splitlines(True)
    for i, line in enumerate(data):
        if line.startswith("version"):
            data[i] = "version: " + target_version + "\n"
with open(galaxy_path, 'w') as f:
    f.writelines(data)

# 4. Update CHANGELOG.rst & galaxy.yml and push a releasing PR
os.system("chmod +x {0}/update_changelog.sh && {1}/update_changelog.sh {2} {3} {4}".format(script_dir, script_dir, directory, pr_name, target_version))
# else:
#     # get latest code after PR merged
#     os.system("chmod +x get_code.sh && ./get_code.sh {0} {1} {2} {3}".format(directory, config['settings']['collection_name'], target_version, remote_branch))
    
#     # 5. Write release body content accoding to changelog.yml
#     with open(change_log_path) as f:
#         dataMap = yaml.safe_load(f)
#         change_content = dataMap['releases'][target_version]['changes']
#     with open("{0}/release_content.txt".format(directory), 'w') as f:
#         f.write("1.	New release v{0}\n2. Changes\n".format(target_version))
#         yaml.dump(change_content, f)
#         f.write("3. Detailed changelog: https://github.com/xinyuezhao/ansible-mso/compare/{0}...v{1}".format(latest_version, target_version))

#     # 6. Public release in github release
#     print("releasing in github release")
#     os.system("chmod +x release_galaxy.sh && ./release_galaxy.sh {0} {1} {2}".format(directory, config['settings']['collection_name'], target_version))

#     # 7. Publish release in Galaxy
#     # ansible-galaxy collection publish xinyuezhao18-mso-1.4.0.tar.gz --api-key=6807bdc1da2e0b2a3f6a132a6daf41e43004a0ec 
#     # by default distribuiting server will be ansible galaxy 

#     # print("releasing in ansible galaxy")
#     # galaxy_key = config['settings']['galaxy_key']
#     # galaxy_ns = config['settings']['galaxy_namespace']
#     # galaxy_path = "{0}-{1}-{2}.tar.gz".format(galaxy_ns, collection, target_version)
#     # os.system("chmod +x galaxy.sh && ./galaxy.sh {0} {1}".format(galaxy_path, galaxy_key))

#     # TODO: add an ansible.cfg file defining server&api-key
    
#     # 8. Publish release in RedHat automation hub
#     # ansible-galaxy collection publish xinyuezhao18-mso-1.4.0.tar.gz --server --api-key=xxx



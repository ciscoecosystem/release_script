# script to collect commit message
#!/usr/bin/python
from simple_term_menu import TerminalMenu
import requests
import sys
import yaml
import configparser
import datetime
import os

config = configparser.ConfigParser()
config.read(sys.argv[1])

repo_url = config['settings']['repo_url']
target_version = config['settings']['target_version']
latest = requests.get('{0}/releases/latest'.format(repo_url))
latest_version = latest.json().get('tag_name')
collection = config['settings']['collection_name']
collection_name = 'ansible-' + collection
url = '{0}/compare/{1}...master'.format(repo_url, latest_version)

r = requests.get(url)
result = r.json()
commits = result.get('commits')

bug = []
minor = []
major = []
untagged = []

# cd to directory of the collection
# directory is absolute path
directory = config['settings']['directory']
remote_branch = config['settings']['remote_branch']
change_log_path = '{0}/changelogs/changelog.yaml'.format(directory)

options = ["Update changelog and create a releasing PR", "Build collection and release"]
terminal_menu = TerminalMenu(options)
menu_entry_index = terminal_menu.show()
if menu_entry_index == 0:
    # 1. Create a new branch release_{target_version} and get latest version
    # os.system("cd {0} && git checkout master && git branch -D release_{1} && git checkout -b release_{2}".format(directory, target_version, target_version))
    os.system("chmod +x release.sh && ./release.sh {0} {1} release_{2}".format(directory, remote_branch, target_version))

    # 2. Update changelog.yml
    # put all commit msg without prefix into untagged list
    for commit in commits:
        commit_message = commit.get('commit').get('message')
        if commit_message.startswith('bugfixes'):
            bug.append(commit_message[len('bugfixes')+2:])
        elif commit_message.startswith('minor_changes'):
            minor.append(commit_message[len('minor_changes')+2:])
        elif commit_message.startswith('major_changes'):
            major.append(commit_message[len('major_changes')+2:])
        elif commit_message.startswith('ignore_changes'):
            pass
        else:
            untagged.append(commit_message)

    release_date = datetime.date.today()

    change_log = dict(
        changes = dict(
            release_summary = 'Release v{0} of the ``{1}`` collection on {2}.\nThis changelog describes all changes made to the modules and plugins included in this collection since {3}.\n'.format(target_version, collection_name, release_date, latest_version)
        ),
        release_date = str(release_date)
    )
    if bug:
        change_log['changes']['bugfixes'] = bug
    if minor:
        change_log['changes']['minor_changes'] = minor
    if major:
        change_log['changes']['major_changes'] = major

    if untagged:
        change_log['changes']['untagged'] = untagged

    with open(change_log_path) as f:
        dataMap = yaml.safe_load(f)
        dataMap['releases'][target_version] = change_log
    with open(change_log_path, 'w') as f:
        yaml.dump(dataMap, f)

    # edit changelog.yaml as we want
    os.system("vim {0}".format(change_log_path))

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
    prName = "release_" + target_version
    os.system("chmod +x update_changelog.sh && ./update_changelog.sh {0} {1}".format(directory, prName))
else:
    # get latest code after PR merged
    os.system("chmod +x get_code.sh && ./get_code.sh {0} {1} {2} {3}".format(directory, config['settings']['collection_name'], target_version, remote_branch))
    
    # 5. Write release body content accoding to changelog.yml
    with open(change_log_path) as f:
        dataMap = yaml.safe_load(f)
        change_content = dataMap['releases'][target_version]['changes']
    with open("{0}/release_content.txt".format(directory), 'w') as f:
        f.write("1.	New release v{0}\n2. Changes\n".format(target_version))
        yaml.dump(change_content, f)
        f.write("3. Detailed changelog: https://github.com/xinyuezhao/ansible-mso/compare/{0}...v{1}".format(latest_version, target_version))

    # 6. Public release in github release
    print("releasing in github release")
    os.system("chmod +x release_galaxy.sh && ./release_galaxy.sh {0} {1} {2}".format(directory, config['settings']['collection_name'], target_version))

    # 7. Publish release in Galaxy
    # ansible-galaxy collection publish xinyuezhao18-mso-1.4.0.tar.gz --api-key=6807bdc1da2e0b2a3f6a132a6daf41e43004a0ec 
    # by default distribuiting server will be ansible galaxy 
    print("releasing in ansible galaxy")
    galaxy_key = config['settings']['galaxy_key']
    galaxy_ns = config['settings']['galaxy_namespace']
    galaxy_path = "{0}-{1}-{2}.tar.gz".format(galaxy_ns, collection, target_version)
    os.system("chmod +x galaxy.sh && ./galaxy.sh {0} {1}".format(galaxy_path, galaxy_key))

    # TODO: add an ansible.cfg file defining server&api-key
    
    # 8. Publish release in RedHat automation hub
    # ansible-galaxy collection publish xinyuezhao18-mso-1.4.0.tar.gz --server --api-key=xxx
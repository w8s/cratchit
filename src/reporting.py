import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time

def report(member, save_dir, graph_file, projects, project_cases, activity_projects, activity_cases, member_repo_list, changeset_list):

    filename = member.history[-1]['date'].strftime("%Y%m%d-%H%M%S-") + member.username + ".md"

    try:
        os.remove(os.path.join(save_dir, filename))
    except OSError:
        pass

    with open(os.path.join(save_dir, filename), 'a') as f:

        f.write("# Weekly Activity Report for %s" % member.name + "\n\n")

        # Write Resolves
        projects_and_cases = [[case for case in project_cases if case['project'] == project] for project in projects]

        header = "## Resolved Cases (" + str(len(project_cases)) + ")"
        f.write(header)

        for project in projects_and_cases:
            title = project[0]['project'] + ' (' + str(len(project)) + ')'
            f.write("\n\n### %s\n\n" % title)
            for case in project:
                f.write("* [%s](%s)  %s  %s\n" % (case['case_num'], case['url'], case['date'].strftime("%m/%d/%Y"), case['title']))

            f.write("")

        # Write Activity
        projects_and_cases = [[case for case in activity_cases if case['project'] == project] for project in activity_projects]

        header = "\n---\n## Case Activity (" + str(len(activity_cases)) + ")"
        f.write(header)

        for project in projects_and_cases:
            title = project[0]['project'] + ' (' + str(len(project)) + ')'
            f.write("\n\n### %s\n\n" % title)
            for case in project:
                f.write("* [%s](%s)  %s\n" % (case['case_num'], case['url'], case['title']))

            f.write("")

        # Write Commits
        commits = 0
        for item in changeset_list:
            for key, value in item.iteritems():
                commits += len(value)

        header = "\n---\n## Commits (%d)" % commits
        f.write(header)

        for repo in member_repo_list:
            changesets = []
            for item in changeset_list:
                changesets = item[repo]

            title = "%s (%d)" % (repo, len(changesets))
            f.write("\n\n### %s\n\n" % title)
            for change in changesets:
                f.write("* [`%s`](%s)  %s  %s\n" % (change['change'], change['url'], change['date'].strftime("%m/%d/%Y"), change['description']))

        # Write Graph
        f.write('\n---\n\n## Graph')
        f.write('\n![Historical Graph](%s)' % graph_file)

    print "Report saved to: %s" % os.path.join(save_dir, filename)


def get_resolved_cases(config, member, begin, end):
    cases_command = 'cmd=search&q=resolved:\'' + end.strftime("%m/%d/%Y") + '..' + begin.strftime("%m/%d/%Y") + '\' resolvedBy:\''+ member.name +'\'&cols=dtResolved,sProject,sTitle'

    cases_url = config['url'] + 'api.asp?' + cases_command + '&token=' + config['token']

    resolved_cases_request = requests.get(cases_url)
    resolved_cases_xml = ET.fromstring(resolved_cases_request.content)

    projects = []
    project_cases = []

    for case in list(resolved_cases_xml[0]):
        time_obj = time.strptime(case.find('dtResolved').text, "%Y-%m-%dT%H:%M:%SZ")

        case_dict = {
                'case_num': case.get('ixBug'),
                'date' : datetime.fromtimestamp(time.mktime(time_obj)),
                'project' : case.find('sProject').text,
                'title' : case.find('sTitle').text,
                'url': 'http://fogbugz.cs2.cert.org/default.asp?' + case.get('ixBug')
            }


        if case_dict['project'] not in projects:
            projects.append(case_dict['project'])

        project_cases.append(case_dict)

    return projects, project_cases


def get_case_activity(config, member, begin, end):

    activity_command = 'cmd=search&q=edited:\'' + end.strftime("%m/%d/%Y") + '..' + begin.strftime("%m/%d/%Y") + '\' EditedBy:\''+ member.name +'\'&cols=dtResolved,sProject,sTitle'

    activity_url = config['url'] + 'api.asp?' + activity_command + '&token=' + config['token']

    activity_request = requests.get(activity_url)

    activity_request_xml = ET.fromstring(activity_request.content)

    projects = []
    activity_cases = []

    for case in list(activity_request_xml[0]):

        case_dict = {
                'case_num': case.get('ixBug'),
                'project' : case.find('sProject').text,
                'title' : case.find('sTitle').text,
                'url': 'http://fogbugz.cs2.cert.org/default.asp?' + case.get('ixBug')
            }


        if case_dict['project'] not in projects:
            projects.append(case_dict['project'])

        activity_cases.append(case_dict)

    return projects, activity_cases


def get_commits(config, member, begin, end):
    repo_url = config['kiln_url'] + "Project/?token=" + config['token']
    repos = requests.get(repo_url)

    repo_list = []

    for project in repos.json():
        for repogroup in project['repoGroups']:
            for repo in repogroup['repos']:
                repo_list.append((repo['ixRepo'], repo['sName']))

    member_repo_list = []
    project_changeset_list = []

    for ixRepo, repoName in repo_list:
        commit_command = 'Search/Changesets?sQuery=edited:"' + end.strftime("%m/%d/%Y") + '..' + begin.strftime("%m/%d/%Y") + '" author:"' + member.username + '"&cHits=10000&ixRepo=' + str(ixRepo)

        commit_url = config['kiln_url'] + commit_command + '&token=' + config['token']

        changesets = requests.get(commit_url)

        if len(changesets.json()['resultChangeset']) > 0:
            member_repo_list.append(repoName)

            project_changeset_dict = {}
            project_changeset_dict[repoName] = []

            for change in changesets.json()['resultChangeset']:
                time_obj = time.strptime(change['dt'], "%Y-%m-%dT%H:%M:%S.%f0ZZ")
                date = datetime.fromtimestamp(time.mktime(time_obj))
                change_dict = {
                    'change' : change['rev'][:12],
                    'date' : date,
                    'description' : change['sDescription'].encode('UTF-8'),
                    'url' : config['url'] + 'kiln/Search?search=' + change['rev'][:12]
                    }

                project_changeset_dict[repoName].append(change_dict)

            project_changeset_list.append(project_changeset_dict)

    return member_repo_list, project_changeset_list


def get_historical_counts(config, member, begin, end):
    # Get resolved count
    cases_command = 'cmd=search&q=resolved:\'' + end.strftime("%m/%d/%Y") + '..' + begin.strftime("%m/%d/%Y") + '\' resolvedBy:\''+ member.name +'\''

    cases_url = config['url'] + 'api.asp?' + cases_command + '&token=' + config['token']

    resolved_cases_request = requests.get(cases_url)
    resolved_cases_xml = ET.fromstring(resolved_cases_request.content)

    resolves = resolved_cases_xml[0].attrib['count']

    # Get activity Count
    activity_command = 'cmd=search&q=edited:\'' + end.strftime("%m/%d/%Y") + '..' + begin.strftime("%m/%d/%Y") + '\' EditedBy:\''+ member.name +'\''

    activity_url = config['url'] + 'api.asp?' + activity_command + '&token=' + config['token']

    activity_request = requests.get(activity_url)

    activity_request_xml = ET.fromstring(activity_request.content)

    activity = activity_request_xml[0].attrib['count']

    # Get commit count
    repo_url = config['kiln_url'] + "Project/?token=" + config['token']
    repos = requests.get(repo_url)

    repo_list = []

    for project in repos.json():
        for repogroup in project['repoGroups']:
            for repo in repogroup['repos']:
                repo_list.append((repo['ixRepo'], repo['sName']))

    commits = 0

    for ixRepo, repoName in repo_list:
        commit_command = 'Search/Changesets?sQuery=edited:"' + end.strftime("%m/%d/%Y") + '..' + begin.strftime("%m/%d/%Y") + '" author:"' + member.username + '"&cHits=10000&ixRepo=' + str(ixRepo)

        commit_url = config['kiln_url'] + commit_command + '&token=' + config['token']

        changesets = requests.get(commit_url)

        if len(changesets.json()['resultChangeset']) > 0:
            commits += len(changesets.json()['resultChangeset'])

    return {'date' : begin,
            'resolves' : resolves,
            'activity' : activity,
            'commits'  : commits}


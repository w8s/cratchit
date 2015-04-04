import xml.etree.ElementTree as ET
import requests
import urllib, random
import shelve
import getpass
import graphing
import os
from datetime import datetime
from model import TeamMember

s = shelve.open('cratchit')

def enter_teammembers():
    print '\nWe are going to enter the names and usernames of your team members.'

    add_users = True

    members = s['members']

    while add_users:
        name = raw_input('\nEnter team member name: ')
        username = raw_input('Enter team member username: ')

        member = TeamMember(name, username)

        members.append(member)

        response = True
        while response:
            more = raw_input('\nDo you want to add more (yes/no): ')
            if more == 'yes':
                response = False

            if more == 'no':
                response = False
                add_users = False

    s['members'] = members


def enter_global_data():
    print 'Configure Cratchit:\n'

    url = raw_input('URL for issue tracker: ')
    print '\nWe need to get a token. In order to do that, we need your username and password. This information will not be stored.\n'
    username = raw_input('Username: ')
    password = getpass.getpass()

    token_url = url + "api.asp?cmd=logon&email=" + username + "&password=" + urllib.quote(password)

    safe_url = url + "api.asp?cmd=logon&email=" + username + "&password=" + "*"*len(password)

    print "\nSending a request to %s to get a token." % safe_url

    token_request = requests.get(token_url)

    response = ET.fromstring(token_request.content)
    token = response.find('token').text.strip()

    print "\nToken received: %s" % token

    home_dir = os.path.expanduser("~")
    cratchit_dir = os.path.join(home_dir, "cratchit")

    config_dict = { 'url'   : url,
                    'token' : token,
                    'home'  : cratchit_dir}

    s['config'] = config_dict


def add_teammembers():
    response = True
    while response:
        answer = raw_input("\nDo you want to add a team member? ")
        if answer != 'no' and answer != 'yes':
            response = True
            print "\nPlease enter 'yes' or 'no'."

        if answer == 'yes':
            response = False
            enter_teammembers()

        if answer == 'no':
            response = False


def generate_reports():
    print '\nGenerating reports for %d team members.' % len(s['members'])

    members = s['members']

    for member in members:
        resolves = int(random.random() * 100)
        activity = int(random.random() * 100)
        commits = int(random.random() * 100)
        print "\nReport for %s:" % member
        # get case resolves
        print 'Resolves: %d' % resolves
        # get case activity
        print 'Activity: %d' % activity
        # get commits
        print 'Commits: %d' % commits

        member.add_overview_data({'date' : datetime.now(),
                                  'resolves' : resolves,
                                  'activity' : activity,
                                  'commits'  : commits})

        save_dir = os.path.join(s['config']['home'], "reports", member.username)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        graphing.graph(member, save_dir)

    s['members'] = members


if 'config' not in s:
    enter_global_data()

if 'members' not in s:
    s['members'] = []

print '\nYou are tracking %d users.' % len(s['members'])

count = 1
for member in s['members']:
    print "%d. %s (%d)" % (count, member, len(member.history))
    count += 1

add_teammembers()

generate_reports()

s.close()

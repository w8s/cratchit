import requests
import urllib

def enter_teammembers():
    print 'We are going to enter the names and usernames of your team members.'

    add_users = True

    while add_users:
        name = raw_input('Enter team member name: ')
        username = raw_input('Enter team member username: ')

        response = True
        while response:
            more = raw_input('Do you want to add more (yes/no): ')
            if more == 'yes':
                response = False

            if more == 'no':
                response = False
                add_users = False

        print "Hi, %s. Your username is %s." % (name, username)


def enter_global_data():
    print 'Configure Cratchit:'

    url = raw_input('URL for issue tracker: ')
    print '\nWe need to get a token. In order to do that, we need your username and password. This information will not be stored.\n'
    username = raw_input('Username: ')
    password = raw_input('Password: ')

    token_url = url + "api.asp?cmd=logon&email=" + username + "&password=" + urllib.quote(password)
    print token_url
    token_request = requests.get(token_url)
    print token_request.text


enter_global_data()

# enter_teammembers()

class TeamMember(object):

    def __init__(self, name, username):
        self.name = name
        self.username = username
        self.history = []

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str('TeamMember(' + self.name + ", " +  self.username + ')')

    def add_overview_data(self, data_dict):
        added = False
        for data in self.history:
            if data_dict['date'].date() == data['date'].date():
                data = data_dict
                added = True

        if not added:
            self.history.append(data_dict)

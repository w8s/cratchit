from datetime import datetime, timedelta
from model import TeamMember
import xml.etree.ElementTree as ET
import reporting
import requests
import shelve

s = shelve.open('cratchit')


members = s['members']

for member in members:

    if len(member.history) < 12:
        last_record_date = member.history[-1]['date']
        last_date = last_record_date - timedelta(days=7)
        one_week = last_date - timedelta(days=7)
        weeks = 12 - len(member.history)

        week = 0
        while week < weeks:
            print "Week %d" % week

            history_dict = reporting.get_historical_counts(s['config'], member, last_date, one_week)
            print history_dict

            member.add_overview_data(history_dict)

            last_date = one_week
            one_week = last_date - timedelta(days=7)
            week += 1

    print member.history

s['members'] = members

s.close()

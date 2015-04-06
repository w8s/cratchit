import matplotlib.pyplot as plt
import datetime
import os
import numpy as np


def graph(member, save_dir):

    time_series = member.history[-12:]

    dates = [entry['date'] for entry in time_series ]
    resolves = [entry['resolves'] for entry in time_series]
    commits = [entry['commits'] for entry in time_series]
    activity = [entry['activity'] for entry in time_series]

    plt.plot_date(dates,resolves, linestyle='-', color='b', label='Resolves')
    plt.plot_date(dates,commits,  linestyle='-', color='r', label='Commits')
    plt.plot_date(dates,activity, linestyle='-', color='g', label='Activity')

    plt.legend(loc="upper left")
    plt.title("3 Month Historical Activity for %s" % member.name)
    plt.xlabel("Date")
    plt.ylabel("Number of Cases/Commits")

    filename = dates[-1].strftime("%Y%m%d-%H%M%S-") + member.username + ".png"

    plt.savefig(os.path.join(save_dir, filename))
    plt.close()

    return os.path.join(save_dir, filename)

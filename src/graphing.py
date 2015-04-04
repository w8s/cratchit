import matplotlib.pyplot as plt
import datetime
import os
import numpy as np


def graph(member, home):

    time_series = member.history

    # dates = [entry['date'] for entry in time_series ][-4:]
    dates = [entry['date'] for entry in time_series ]
    resolves = [entry['resolves'] for entry in time_series]
    commits = [entry['commits'] for entry in time_series]
    activity = [entry['activity'] for entry in time_series]

    plt.plot_date(dates,resolves, linestyle='-', color='b')
    plt.plot_date(dates,commits,  linestyle='-', color='r')
    plt.plot_date(dates,activity, linestyle='-', color='g')

    filename = dates[-1].strftime("%Y%m%d-%H%I%S-") + member.username + ".png"
    save_dir = os.path.join(home, "reports", member.username)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    plt.savefig(os.path.join(save_dir, filename))

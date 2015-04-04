import matplotlib.pyplot as plt
import datetime
import os
import numpy as np


def graph(member, save_dir):

    time_series = member.history

    # dates = [entry['date'] for entry in time_series ][-4:]
    dates = [entry['date'] for entry in time_series ]
    resolves = [entry['resolves'] for entry in time_series]
    commits = [entry['commits'] for entry in time_series]
    activity = [entry['activity'] for entry in time_series]

    plt.plot_date(dates,resolves, linestyle='-', color='b')
    plt.plot_date(dates,commits,  linestyle='-', color='r')
    plt.plot_date(dates,activity, linestyle='-', color='g')

    filename = dates[-1].strftime("%Y%m%d-%H%M%S-") + member.username + ".png"

    plt.savefig(os.path.join(save_dir, filename))

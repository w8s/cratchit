import os

def report(member, save_dir, graph_file):

    filename = member.history[-1]['date'].strftime("%Y%m%d-%H%M%S-") + member.username + ".txt"

    with open(os.path.join(save_dir, filename), 'a') as f:

        [f.write('%s\n%s\n\nResolves: %d\nActivity: %d\nCommits: %d\n\n' % (entry['date'].strftime("%m/%d/%Y"), '='*len(entry['date'].strftime("%m/%d/%Y")), entry['resolves'], entry['activity'], entry['commits'] )) for entry in member.history]

        f.write('\n![Historical Graph](%s)' % graph_file)

import os
import sqlite3
import time
import datetime
import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from matplotlib.patches import Rectangle
from matplotlib import style
style.use('fivethirtyeight')


def graph_trace(conn, tracename, image_dir):
    c = conn.cursor()

    # Plot master data - Date of trace vs FPS
    # The checks for NULL are meant to include records before those columns were added.
    # The NULL checks can be removed after there are more than 30 records with the new columns.
    query = 'SELECT Date, FPS FROM results'
    query += ' WHERE TraceName = ' + '"' + tracename + '"'
    query += ' AND (VVLBranch = "master" OR VVLBranch IS NULL)'
    query += ' AND (VVLRepo = "https://github.com/KhronosGroup/Vulkan-ValidationLayers.git" OR VVLRepo IS NULL)'
    query += ' ORDER BY Date DESC LIMIT 30'
    c.execute(query)
    data = c.fetchall()
    master_dates = []
    values = []
    for row in data:
        master_dates.append(parser.parse(row[0]))
        values.append(row[1])
    plt.plot_date(master_dates, values, 'bo', label='master', color='blue')

    # Plot developer submissions - only those within the range of the master data.
    # We'll miss the ones that were made before the new columns were added, but that is OK.
    start_date = min(master_dates)
    query = 'SELECT Date, FPS FROM results'
    query += ' WHERE TraceName = ' + '"' + tracename + '"'
    query += ' AND'
    query += '  ('
    query += '   VVLBranch != "master"'
    query += '   OR'
    query += '   VVLRepo != "https://github.com/KhronosGroup/Vulkan-ValidationLayers.git"'
    query += '  )'
    query += ' AND Date >= ' + '"' + \
        start_date.strftime("%Y-%m-%d %H:%M:%S") + '"'
    c.execute(query)
    data = c.fetchall()
    dev_dates = []
    values = []
    for row in data:
        dev_dates.append(parser.parse(row[0]))
        values.append(row[1])
    plt.plot_date(dev_dates, values, 'bo', label='developer', color='orange')

    # A "correct" database has exactly one result marked as the baseline.
    # Plot the baseline only if there is exactly one.
    c.execute('SELECT FPS FROM results WHERE TraceName = "' +
              tracename + '" AND Baseline = 1')
    baseline_data = c.fetchall()
    if (len(baseline_data) == 1):
        combined_dates = master_dates + dev_dates
        row = baseline_data[0]
        FPS = row[0]
        baseline_dates = [min(combined_dates), max(combined_dates)]
        baseline_values = [FPS, FPS]
        plt.plot_date(baseline_dates, baseline_values, '-', label='baseline')
        ax = plt.gca()
        rect = Rectangle((min(combined_dates), FPS * 0.95), max(combined_dates) -
                         min(combined_dates), FPS * 0.05, color='green', alpha=0.5)
        ax.add_patch(rect)

    plt.title(tracename, loc='left', fontsize=18)
    plt.title('on perfwinnvi', loc='right', fontsize=13)
    plt.xlabel("Date")
    plt.xticks(rotation=90)
    plt.ylabel("FPS")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(image_dir, tracename + ".png"))
    plt.close()


def graph_traces(db_file, image_dir):
    trace_names = []
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT DISTINCT TraceName FROM results ORDER BY TraceName')
    data = c.fetchall()
    for row in data:
        trace_name = row[0]
        graph_trace(conn, trace_name, image_dir)
        trace_names.append(trace_name)
    c.close
    conn.close()
    return trace_names


if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.realpath(__file__))
    db_file = os.path.join(script_dir, "database", "PerfResultsDB.db")
    image_dir = os.path.join(script_dir, "generated_images")
    graph_traces(db_file, image_dir)

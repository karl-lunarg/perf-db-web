import os
import sqlite3
import time
import datetime
import random

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from matplotlib import style
style.use('fivethirtyeight')

def graph_trace(conn, tracename, image_dir):
    c = conn.cursor()

    # Plot main data - Date of trace vs FPS
    c.execute('SELECT Date, FPS FROM results WHERE TraceName = ' + '"' + tracename + '"')
    data = c.fetchall()
    dates = []
    values = []
    for row in data:
        dates.append(parser.parse(row[0]))
        values.append(row[1])
    plt.plot_date(dates, values, 'bo', label='trace')

    # A "correct" database has exactly one result marked as the baseline.
    # Plot the baseline only if there is exactly one.
    c.execute('SELECT FPS FROM results WHERE TraceName = "' + tracename + '" AND Baseline = 1')
    baseline_data = c.fetchall()
    if (len(baseline_data) == 1):
        row = baseline_data[0]
        FPS = row[0]
        baseline_dates = [min(dates), max(dates)]
        baseline_values = [FPS, FPS]
        plt.plot_date(baseline_dates, baseline_values, '-', label='baseline')

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

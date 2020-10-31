import sqlite3
import json
import os
import plotperf

from flask import Flask, request, send_file, redirect, url_for
from connection.sqlite3_connection import Sqlite3Connection, sqlite3_call


app = Flask(__name__)

# Tell the browser to not cache images
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    response.cache_control.public = True
    return response

@app.route("/")
def main():
    index_path = os.path.join(app.static_folder, "index.html")

    # Generate the plot images
    database_path = os.path.join(app.root_path, "database", "PerfResultsDB.db")
    images_path = os.path.join(app.root_path, "generated_images")
    trace_names = plotperf.graph_traces(database_path, images_path)

    # Read the index.html file so we can modify it on the way to the server.
    # We need to insert HTML to display the images we just generated.
    # The number of images is unknown as it depends on what is in the database
    # and so cannot be hard-coded.
    with open(index_path, 'r') as file:
        html = file.readlines()

    # Find the image insert point
    indices = [i for i, s in enumerate(html) if '<!-- Image Insert Point -->' in s]

    # There is no easy way to get a list of the image files we just generated.
    # (We can't embed javascript in index.html to get the list on the server side.)
    # So use the list returned by plotperf to generate the HTML needed to render the images.
    # Hard-coded to 2 images per row.
    if len(indices) == 1:
        image_html = ['<div class="perf_image_row">']
        for i in range(len(trace_names)):
            name = trace_names[i]
            if i % 2 == 0:
                image_html.append('<div class="perf_image_col">')
            image_html.append('<img src="/generated_images/'+name+'.png" alt="'+name+'">')
            if i % 2 == 1:
                image_html.append('</div>')
        if len(trace_names) % 2 == 1:
            image_html.append('</div>')
        image_html.append('</div>')
        html[indices[0]:indices[0]] = image_html
    return ''.join(html)

@app.route("/generated_images/<path:path>")
def images(path):
    fullpath = "./generated_images/" + path
    return send_file(fullpath, mimetype='image/png')

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='LunarG-icon-blue-on-white.png'))


@app.route("/run", methods=["POST", "GET"])
def run():
    """
    In this function the connection is open and closed with every call -> inefficient
    """
    path = "./database/PerfResultsDB.db"
    query = ""

    database = Sqlite3Connection(path)
    database.open()

    # extract query parameters
    if request.method == "GET":
        query = request.args.get("query")
    elif request.method == "POST":
        query = request.form["query"]

    try:
        result = sqlite3_call(database, query)
        output = json.dumps(result)
    except sqlite3.Error as err:
        output = err.args[0]

    database.close()
    return output


if __name__ == "__main__":
    # Only for debugging while developing and running main.py (without docker):
    # -> choose a port higher than 1000 to avoid permission problems
    #app.run(host="0.0.0.0", port=5000, debug=True)
    # Port 80 configuration to run via docker-compose up
    app.run(host="0.0.0.0", port=80, debug=True)

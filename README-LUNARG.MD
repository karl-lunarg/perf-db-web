# LunarG-Specific Notes

This repository is a fork of the [example
repository](https://github.com/maltesander/uwsgi-nginx-flask-python-sqlite-docker-example)
for making a Docker container that contains a web server running a Flask web
application that interfaces with an SQLite database. There is a
[tutorial](https://tutorial-academy.com/uwsgi-nginx-flask-python-sqlite-docker-example/)
for this example repository.

The main purpose is to read a database containing performance stats and display
them in with a web server.  The web server and associated components are all
encapsulated in a Docker container.

## Deployment

Install:

```sh
docker
docker-compose
```

Clone this repository and run:

```sh
docker-compose --file docker-compose.override.yml --project-name val_perf build
```

This should create a Docker image called `val_perf_web` which you can see with
`docker images`.

Then start the container with:

```sh
docker run --rm --detach --publish 5080:80 --name perf val_perf_web
```

This will start the server on port 5080 (`http://localhost:5080`).

## TO DO Database Installation

For now, we're using a copy of the performance data database for development
that is checked into this repository and accessed by the web application.
Eventually, we want the Docker container to use a volume to access the database
file, which will be updated periodically outside of the container.

## Development

It is a bit tricky to work on the code in this environment because you can't
change things easily in a running container and it is time consuming to stop,
rebuild, and start containers.

You can login to a running container to check things out with:

```sh
docker exec -it perf /bin/bash
```

One approach is to have the container run code out of the `app` tree and not
from inside the container by adding `--volume pwd/app:/app` to the `docker
run` command.  This works, except that I don't know how to get the python code
to rebuild if it is changed.  It is possible to change `index.html` and see the
changes take effect by refreshing the browser.  But this is not that useful.

A better approach is to run the Flask app completely outside of the container,
and thus, outside of Docker.  Watch out for port conflicts between running
containers and starting the Flask app outside of the container.

Install the python Flask (web application framework) package with:

```sh
sudo pip3 install Flask
```

You need to do this because the container itself already has Flask configured
inside of it and if you intend to run the Flask-based application, you'll need a
local installation of Flask.  You need to do it as root if you want to use a
port < 1000 since you'll need to run the application as root in that case.

And then change to the `app` directory and run the main application:

```sh
python3 main.py
or
sudo python3 main.py
```

Look at the bottom for comments and notes about setting the port and running the
app standalone.

This is much better in that you can see messages from the server that can be
helpful and it gives you a debugger PIN that presumably lets you attach a
debugger.  I haven't tried this.

But if you modify a python file, the server sees that and re-compiles the file.
This makes it very easy to change all the web application code and see the
changes immediately.

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

These instructions are for Linux.  It is unknown how well this would all work on
Windows, but since it is Docker and most of the code is not platform-specific,
there is a good change that it could run in a Docker container on Windows (not
tried yet).

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

### Database Installation

Of course the web application needs to access a database outside the container.
The application expects to find the database in `/app/database` within the
container's file system. This repository includes a sample database in
`/app/database` which can be used for bring-up purposes.  But you will want to
use an external database file instead.

The volume option on `docker run` "mounts" a host
file system directory on top of a directory in the container's file system.  For
example, this option mounts the host's `/mnt/perf_database` on top of the
container's `/app/database` directory:

```sh
--volume /mnt/perf_database:/app/database
```

 `/mnt/perf_database` may be a good place for a Linux machine to keep the
 database because this could be where the Linux machine has mounted an
 external file share that holds the database.

### Starting the Server

Start the container with:

```sh
docker run --restart always --detach --publish 5080:80 --name perf --volume /mnt/perf_database:/app/database val_perf_web
```

This will start the server on port 5080 (`http://localhost:5080`).

The container can be stopped with:

```sh
docker stop perf
```

## Development

### Inside of Docker (not the best)

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

### Outside of the container (better)

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

FROM tiangolo/uwsgi-nginx-flask:python3.8
# STATIC_INDEX 1 will force the nginx server to serve index.html directly
# instead of calling the function in main.py decorated with route("/").
# We want to process index.html in main.py so, set it to 0 here.
ENV STATIC_INDEX 0
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./app /app

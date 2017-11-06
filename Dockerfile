FROM tiangolo/uwsgi-nginx-flask:python2.7
COPY ./api /app
ADD requirements.txt /app
RUN pip install -r requirements.txt
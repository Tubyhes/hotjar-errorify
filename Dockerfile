FROM tiangolo/uwsgi-nginx-flask:python2.7
ADD errorify.conf /etc/nginx/conf.d/
COPY ./api /app
ADD kubernetes_settings.py /app
ENV ERRORIFY_SETTINGS /app/kubernetes_settings.py
ADD requirements.txt /app
RUN pip install -r requirements.txt

======================dockerfile
FROM python:3.9.5-slim-buster

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt


COPY . /usr/src/app

EXPOSE 80
CMD ["python", "manage.py", "runserver"]

==========================================================
service port 80
Su dung docker de build 
- docker build -t mypt_notification .
Run container
- docker run -d -p 80:80 mypt_noti


cac bien moi truong :
MYSQL_DATABASE_HOST
MYSQL_DATABASE_USER
MYSQL_DATABASE_PASSWORD
MYSQL_DATABASE_DB
MYSQL_DATABASE_PORT
USE_PRODUCTION

bien USE_PRODUCTION de phan biet moi truong stagging va production , USE_PRODUCTION = 1 là moi truong product , USE_PRODUCTION= 0 la moi truong stagging.

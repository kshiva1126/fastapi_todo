FROM python:3.8.3
RUN apt-get update ; apt-get install -y libpq-dev
COPY requirements.txt /tmp/
RUN pip install  --requirement /tmp/requirements.txt
COPY . /tmp/
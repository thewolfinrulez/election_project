FROM python:3.11

RUN apt-get update && apt-get install -y cron

ENV CONTAINER_HOME=/var/www
COPY requirements.txt $CONTAINER_HOME/
RUN pip install -r $CONTAINER_HOME/requirements.txt

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

CMD ["python", "main.py"]
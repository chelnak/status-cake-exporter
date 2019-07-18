FROM python:3.7.4-alpine3.10

ADD exporter exporter/
add requirements.txt exporter/requirements.txt

WORKDIR exporter

RUN pip install -r requirements.txt

CMD ["python", "app.py"]
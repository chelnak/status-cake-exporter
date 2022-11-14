FROM python:3.10-alpine

COPY dist/ /tmp/
RUN pip install --no-cache-dir /tmp/status_cake_exporter*.whl

EXPOSE 8000

ENTRYPOINT ["status-cake-exporter"]

FROM python:3.10-alpine as build

RUN pip install poetry

WORKDIR /build
COPY . .
RUN poetry install
RUN poetry build

FROM python:3.10-alpine
COPY --from=build /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/status_cake_exporter*.whl
RUN pip install -U python-dateutil
EXPOSE 8000
ENTRYPOINT ["status-cake-exporter"]
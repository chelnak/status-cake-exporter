# Status Cake Exporter

![status-cake-exporter](https://github.com/chelnak/status-cake-exporter/actions/workflows/ci.yml/badge.svg)

> :rotating_light: Container images have moved to ghcr.io/chelnak/status-cake-exporter

Status Cake Exporter is a Prometheus exporter for [StatusCake](https://www.statuscake.com/).

Metrics are exposed on port 8000 when using the provided examples/manifest.yml](examples/manifest.yml) in Kubernetes, e.g.

```sh
http://status-cake-exporter.default.svc:8000
```

## Requirements

* Python 3.7 (not tested with anything below this)
* Python dependencies from `requirements.txt`
* Docker
* Kubernetes (optional)
* Helm 3 (optional)

## Usage

| Setting  | Required | Default |
|----------|----------|---------|
| USERNAME | Yes      | Null    |
| API_KEY  | Yes      | Null    |
| TAGS     | No       | Null    |
| LOG_LEVEL| No       | info    |
| PORT     | No       | 8000    |

### Docker

The following will expose the exporter at `localhost:8000`:

```sh
export USERNAME=statuscakeuser
export API_KEY=xxxxxxxx
docker run -d -p 8000:8000 --env USERNAME --env API_KEY chelnak/status-cake-exporter:latest
```

### Kubernetes

To get up and running quickly, use [examples/manifest.yml](examples/manifest.yml) as an example. You will need to create a secret named `status-cake-api-token` containing your `USERNAME` and `API_KEY` first.

Otherwise, you can use the Helm Chart provided in [chart/status-cake-exporter](chart/status-cake-exporter/README.md).

### Terminal

```sh
usage: app.py [-h] [--username USERNAME] [--api-key API_KEY]
              [--tests.tags TAGS] [--logging.level {debug,info,warn,error}] [--port PORT]

If an arg is specified in more than one place, then commandline values
override environment variables which override defaults.

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   Username for the account [env var: USERNAME]
  --api-key API_KEY     API key for the account [env var: API_KEY]
  --tests.tags TAGS     A comma separated list of tags used to filter tests returned from the api [env var: TAGS]
  --logging.level       {debug,info,warn,error} Set a log level for the application [env var: LOG_LEVEL]
  --port                The TCP port to start the web server on [env var: PORT]
```

## Metrics

| Name| Type | Description |
|-----|------|-------------|
| status_cake_test_info | Gauge |A basic listing of the tests under the current account. |
| status_cake_test_uptime_percent | Gauge | Tests and their uptime percentage |

## Prometheus

Prometheus config needs to be updated in order to see the new exported. Use the following scrape config as an example:

```Yaml
scrape_configs:
    - job_name: status-cake-exporter
    honor_timestamps: true
    scrape_interval: 10m
    scrape_timeout: 1m
    metrics_path: /
    scheme: http
    static_configs:
    - targets:
        - status-cake-exporter.default.svc:8000
```

## Grafana

Data collected by Prometheus can be easily surfaced in Grafana.

Using the [Statusmap panel](https://grafana.com/grafana/plugins/flant-statusmap-panel) by [flant](https://github.com/flant/grafana-statusmap) you can create a basic status visualization based on uptime percentage:

![grafan](examples/grafana.png)

### PromQL

```PromQL
status_cake_test_info * on(test_id) group_right(test_name) status_cake_test_uptime_percent
```

## Development

This repository uses [Tilt](https://tilt.dev) for rapid development on Kubernetes.

To use this, run:

```sh
cd chart/status-cake-exporter
tilt up
```

Tilt will reload your environment when it detects changes to your code.

Note: You will need to provide valid credentials for StatusCake in your `Tiltfile` for this to work.

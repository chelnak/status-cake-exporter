# Statuscake Prometheus Exporter Helm Chart

This Helm chart deploys the StatusCake Prometheus exporter from [chelnak/status-cake-exporter](https://github.com/chelnak/status-cake-exporter).

## Requirements

* Statuscake `username` and `apiKey` defined in [values.yaml](values.yaml).

## Usage

Create your own `values.yaml` file and run:

```bash
helm install status-cake-exporter . --namespace default --values values.yaml
```

## Testing

```bash
helm test ${releaseName}
```

## Development

This repository uses [Tilt](https://tilt.dev) for rapid development on Kubernetes.

To use this, run:

```sh
tilt up
```

Tilt will reload your environment when it detects changes to your code (see [Tiltfile](Tiltfile) for the list of paths watched).

Note: You will need to provide valid credentials for StatusCake in your `Tiltfile` for this to work. To do so, you can copy the file to e.g. `Tiltfile_secret`, update it and then start tilt with:

```sh
tilt up -f Tiltfile_secret
```

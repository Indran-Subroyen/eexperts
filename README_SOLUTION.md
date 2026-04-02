# GitHub Gists API

A simple HTTP API that returns a GitHub user's public gists.

## Quick start with Make

```bash
make build        # build the Docker image
make run          # run the container on port 8080
make setup        # create venv and install dev dependencies
make test         # run the test suite
```

## Quick start with Docker

```bash
docker build -t eexperts-test-api .
docker run -p 8080:8080 eexperts-test-api
```

Then in another terminal:

```bash
curl http://localhost:8080/octocat
```

## Quick start without Docker

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python app.py
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Usage

```
GET /<username>                          — returns the user's public gists as JSON
GET /<username>?page=2&per_page=5        — paginated results
GET /healthz                             — health check
```

### Example

```bash
curl http://localhost:8080/octocat
```

```json
[
  {
    "id": "6cad326836d38bd3a7ae",
    "description": "Hello World",
    "url": "https://gist.github.com/6cad326836d38bd3a7ae",
    "files": ["hello_world.rb"],
    "created_at": "2010-04-14T02:15:15Z",
    "updated_at": "2023-12-12T12:30:00Z"
  }
]
```

## Deploy to Kubernetes (local)

Requires [kind](https://kind.sigs.k8s.io/) and `kubectl`.

```bash
# create a local cluster
kind create cluster

# load the Docker image into the cluster
kind load docker-image eexperts-test-api:latest

# deploy the app (2 replicas with health checks)
kubectl apply -f k8s/

# check pods are running
kubectl get pods

# expose the service locally
kubectl port-forward svc/gists-api 9090:80

# test it
curl http://localhost:9090/octocat
```

### K8s manifests

| File | Purpose |
|------|---------|
| `k8s/deployment.yaml` | 2 replicas, readiness/liveness probes on `/healthz`, resource limits |
| `k8s/service.yaml` | NodePort service routing port 80 to container port 8080 |

### Cleanup

```bash
kubectl delete -f k8s/
kind delete cluster
```

## Extras

- **Caching**: Responses are cached in memory for 60 seconds per user/page combination to reduce calls to the GitHub API.
- **Pagination**: Pass `page` and `per_page` query params to control results.
- **Rate-limit handling**: GitHub 403 rate-limit responses are returned as a friendly 429 with retry info.

## Optional: GitHub token

To avoid GitHub API rate limits (60 requests/hour unauthenticated), set a token:

```bash
# Docker
docker run -p 8080:8080 -e GITHUB_TOKEN=ghp_... eexperts-test-api

# Local
export GITHUB_TOKEN=ghp_...
python app.py
```
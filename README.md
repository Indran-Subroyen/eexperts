# GitHub Gists API

A simple HTTP API that returns a GitHub user's public gists.

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
pip install -r requirements.txt
python app.py
```

## Running tests

```bash
pip install -r requirements.txt
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

## Caching

Responses are cached in memory for 60 seconds per user/page combination to reduce calls to the GitHub API.

## Optional: GitHub token

To avoid GitHub API rate limits (60 requests/hour unauthenticated), set a token:

```bash
# Docker
docker run -p 8080:8080 -e GITHUB_TOKEN=ghp_... eexperts-test-api

# Local
export GITHUB_TOKEN=ghp_...
python app.py
```

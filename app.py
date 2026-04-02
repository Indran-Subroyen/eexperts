import os
import time

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

GITHUB_API = "https://api.github.com"
CACHE_TTL = 60  # keep cached responses for 60s to avoid hammering the API

# simple in-memory cache — good enough for a single-instance server
_cache = {}


def cache_get(key):
    entry = _cache.get(key)
    if entry and time.time() - entry["time"] < CACHE_TTL:
        return entry["data"]
    return None


def cache_set(key, data):
    _cache[key] = {"data": data, "time": time.time()}


def github_headers():
    # use token if available, otherwise we're limited to 60 req/hr
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.route("/<username>")
def user_gists(username):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 30, type=int)

    # check cache first so we don't waste API calls
    cache_key = f"{username}:{page}:{per_page}"
    cached = cache_get(cache_key)
    if cached is not None:
        return jsonify(cached)

    resp = requests.get(
        f"{GITHUB_API}/users/{username}/gists",
        headers=github_headers(),
        params={"page": page, "per_page": per_page},
        timeout=10,
    )

    if resp.status_code == 404:
        return jsonify({"error": f"User '{username}' not found"}), 404

    if resp.status_code == 403:
        # GitHub rate-limits anonymous requests to 60/hr
        retry_after = resp.headers.get("Retry-After", "unknown")
        return jsonify({
            "error": "GitHub API rate limit exceeded",
            "retry_after_seconds": retry_after,
        }), 429

    resp.raise_for_status()

    # pull out only the fields we care about(I selected a few only)
    gists = [
        {
            "id": g["id"],
            "description": g["description"],
            "url": g["html_url"],
            "files": list(g["files"].keys()),
            "created_at": g["created_at"],
            "updated_at": g["updated_at"],
        }
        for g in resp.json()
    ]

    cache_set(cache_key, gists)
    return jsonify(gists)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

import os
import time
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
USER_AGENT = os.getenv(
    "REDDIT_USER_AGENT",
    "web:reddit-public-profile-tracker:1.0 (by /u/YOUR_REDDIT_USERNAME)",
)

_token_cache = {"token": None, "expires_at": 0}


def get_access_token():
    """Get an application-only OAuth token from Reddit."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError(
            "Missing REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET environment variables."
        )

    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        headers={"User-Agent": USER_AGENT},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = now + int(data.get("expires_in", 3600))
    return _token_cache["token"]


def get_public_profile(username):
    """Read only basic public profile metadata for one Reddit username."""
    username = username.strip().removeprefix("u/").strip("/")
    if not username:
        raise ValueError("Username is required.")

    token = get_access_token()

    response = requests.get(
        f"https://oauth.reddit.com/user/{username}/about",
        headers={
            "Authorization": f"bearer {token}",
            "User-Agent": USER_AGENT,
        },
        timeout=15,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    data = response.json().get("data", {})

    created_utc = data.get("created_utc")
    created_iso = None
    if created_utc:
        created_iso = datetime.fromtimestamp(
            created_utc, tz=timezone.utc
        ).isoformat()

    # Keep only the small set of fields needed by this demo.
    return {
        "username": data.get("name"),
        "total_karma": data.get("total_karma"),
        "post_karma": data.get("link_karma"),
        "comment_karma": data.get("comment_karma"),
        "created_utc": created_utc,
        "created_iso": created_iso,
    }


PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Reddit Public Profile Tracker</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; max-width: 760px; margin: 48px auto; padding: 0 20px; }
    input, button { font-size: 16px; padding: 10px; }
    input { width: 65%; }
    button { cursor: pointer; }
    .card { margin-top: 24px; padding: 18px; border: 1px solid #ddd; border-radius: 10px; }
    .error { color: #a00; }
    .muted { color: #666; font-size: 14px; }
  </style>
</head>
<body>
  <h1>Reddit Public Profile Tracker</h1>
  <p class="muted">
    Read-only demo. It retrieves only basic publicly available profile metadata.
  </p>

  <form method="get">
    <input name="username" placeholder="Reddit username" value="{{ username or '' }}" required>
    <button type="submit">Check profile</button>
  </form>

  {% if error %}
    <p class="error">{{ error }}</p>
  {% endif %}

  {% if profile %}
    <div class="card">
      <h2>u/{{ profile.username }}</h2>
      <p><strong>Total karma:</strong> {{ profile.total_karma }}</p>
      <p><strong>Post karma:</strong> {{ profile.post_karma }}</p>
      <p><strong>Comment karma:</strong> {{ profile.comment_karma }}</p>
      <p><strong>Created:</strong> {{ profile.created_iso }}</p>
    </div>
  {% endif %}
</body>
</html>
"""


@app.route("/")
def index():
    username = request.args.get("username", "").strip()
    profile = None
    error = None

    if username:
        try:
            profile = get_public_profile(username)
            if profile is None:
                error = "Profile not found."
        except Exception as exc:
            error = str(exc)

    return render_template_string(
        PAGE,
        username=username,
        profile=profile,
        error=error,
    )


@app.route("/api/profile/<username>")
def api_profile(username):
    try:
        profile = get_public_profile(username)
        if profile is None:
            return jsonify({"error": "Profile not found"}), 404
        return jsonify(profile)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=False)

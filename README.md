# Reddit Public Profile Tracker

A small, private, non-commercial, read-only demo dashboard for retrieving basic publicly available Reddit profile statistics.

## Purpose

The project is designed to monitor a predefined list of Reddit usernames that the operator owns or is authorized to manage.

It retrieves only a limited set of public profile fields:

- Username
- Total karma
- Post karma
- Comment karma
- Account creation date

The project does **not** post, comment, vote, send messages, moderate communities, create accounts, or perform automated actions on behalf of Reddit users.

## How it works

1. The server obtains an application-only OAuth token from Reddit.
2. The server calls Reddit's public user profile endpoint for a supplied username.
3. Only the small set of fields listed above is returned to the local dashboard.

OAuth requests use:

- `POST https://www.reddit.com/api/v1/access_token`
- `GET https://oauth.reddit.com/user/{username}/about`

The project is intended to be used only after Reddit grants the required API access and credentials.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set environment variables

Copy `.env.example` values into your environment:

```text
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USER_AGENT=web:reddit-public-profile-tracker:1.0 (by /u/YOUR_REDDIT_USERNAME)
```

Never commit your real client secret to GitHub.

### 3. Run

```bash
python app.py
```

Open:

```text
http://127.0.0.1:8080
```

## API example

```text
GET /api/profile/spez
```

Example response:

```json
{
  "username": "example",
  "total_karma": 1234,
  "post_karma": 500,
  "comment_karma": 734,
  "created_utc": 1234567890,
  "created_iso": "2009-02-13T23:31:30+00:00"
}
```

## Data access scope

This project is strictly read-only.

It does not:

- Create posts or comments
- Vote
- Send private messages or chats
- Moderate communities
- Join or leave communities
- Create Reddit accounts
- Perform automated actions on behalf of Reddit users
- Scrape Reddit outside the approved API
- Sell or redistribute Reddit data
- Use Reddit data for advertising
- Use Reddit data for AI or machine-learning training
- Use Reddit data for spam or unsolicited outreach

Only the minimum public profile data needed by the dashboard is requested.

## Why Devvit is not used

This is a standalone server-side dashboard that runs outside Reddit. It is not a subreddit application, moderation tool, or Reddit UI experience. It only needs limited read-only access to public user profile metadata.

## Security

API credentials are loaded from environment variables and are never embedded in the source code.

## Status

Prototype / API access request demo.

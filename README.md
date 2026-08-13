# Daily Data Engineering Automation

Automated daily LinkedIn posting + job search alerts for Senior Data Engineering roles.

## What This Does

| Feature | Schedule | How |
|---------|----------|-----|
| LinkedIn Post (DE content) | Daily 8am IST | GitHub Actions + LinkedIn API |
| Job Search Email | Daily 9am IST | Google Custom Search API + Gmail |

## Setup (One-Time)

### 1. GitHub Secrets Required

Go to: `https://github.com/ranganaik/daily-de-automation/settings/secrets/actions`

Add these secrets:

| Secret Name | Where to get it |
|-------------|----------------|
| `LINKEDIN_ACCESS_TOKEN` | From LinkedIn OAuth (expires every 60 days) |
| `LINKEDIN_PERSON_URN` | `urn:li:person:PFESNi6jid` |
| `GOOGLE_CSE_API_KEY` | https://console.cloud.google.com/apis/credentials |
| `GOOGLE_CSE_ID` | https://programmablesearchengine.google.com/ |
| `GMAIL_APP_PASSWORD` | Gmail → Security → App Passwords |
| `EMAIL_TO` | `ranga.k565@gmail.com` |

### 2. Google Custom Search Setup (5 minutes)

1. Go to https://programmablesearchengine.google.com/
2. Create a new search engine
3. Sites to search: `linkedin.com/jobs/*, indeed.com/*, naukri.com/*, glassdoor.com/*`
4. Get the **Search Engine ID** (cx)
5. Go to https://console.cloud.google.com/apis/credentials
6. Create an API key for "Custom Search JSON API"
7. Enable the Custom Search API

### 3. Gmail App Password

1. Go to Google Account → Security → 2-Step Verification (enable if not)
2. Go to https://myaccount.google.com/apppasswords
3. Create app password for "Mail"
4. Copy the 16-char password → save as `GMAIL_APP_PASSWORD` secret

### 4. LinkedIn Token Refresh (every 60 days)

Token expires ~Oct 12, 2026. When it expires:
1. Open the OAuth URL in browser
2. Copy the new code
3. Run the token exchange
4. Update `LINKEDIN_ACCESS_TOKEN` secret in GitHub

## Folder Structure

```
├── .github/workflows/
│   ├── linkedin-daily.yml    # Posts to LinkedIn daily
│   └── job-search-daily.yml  # Searches jobs, emails results
├── linkedin-posts/
│   ├── topics.json           # 30+ topics with content
│   └── post_to_linkedin.py   # Posting script
├── job-finder/
│   ├── search_jobs.py        # Google CSE search + email
│   └── keywords.json         # Search queries
├── resume/
│   └── (your resume PDF)
└── README.md
```

## Cost

| Item | Cost |
|------|------|
| GitHub Actions | Free (2000 min/month) |
| Google Custom Search | Free (100 searches/day) |
| LinkedIn API | Free |
| Gmail SMTP | Free |
| **Total** | **$0/month** |

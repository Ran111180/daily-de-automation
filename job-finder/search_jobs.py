import json
import os
import smtplib
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configuration
EMAIL_TO = os.environ.get("EMAIL_TO", "ranga.k565@gmail.com")
GMAIL_USER = os.environ.get("EMAIL_TO", "ranga.k565@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# Keywords to filter relevant jobs
KEYWORDS = ["data engineer", "snowflake", "databricks", "dbt", "spark", 
            "airflow", "python", "aws", "etl", "data platform", "analytics engineer"]

# Free job RSS feeds and APIs
JOB_SOURCES = [
    {
        "name": "RemoteOK",
        "url": "https://remoteok.com/remote-data-jobs.json",
        "type": "json"
    },
    {
        "name": "Remotive",
        "url": "https://remotive.com/api/remote-jobs?category=data&limit=20",
        "type": "json"
    },
    {
        "name": "HN Who's Hiring (GitHub)",
        "url": "https://hacker-news.firebaseio.com/v0/jobstories.json",
        "type": "hn"
    }
]


def fetch_remoteok_jobs():
    """Fetch from RemoteOK (free JSON API)."""
    jobs = []
    try:
        req = urllib.request.Request(
            "https://remoteok.com/remote-data-jobs.json",
            headers={"User-Agent": "JobSearchBot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            # First item is metadata, skip it
            for item in data[1:20]:
                title = item.get("position", "")
                company = item.get("company", "")
                url = item.get("url", "")
                tags = " ".join(item.get("tags", []))
                date = item.get("date", "")
                
                # Filter by keywords
                search_text = f"{title} {company} {tags}".lower()
                if any(kw in search_text for kw in KEYWORDS):
                    jobs.append({
                        "title": f"{title} at {company}",
                        "link": url,
                        "source": "RemoteOK",
                        "date": date[:10] if date else ""
                    })
    except Exception as e:
        print(f"  RemoteOK error: {e}")
    return jobs


def fetch_remotive_jobs():
    """Fetch from Remotive (free API)."""
    jobs = []
    try:
        req = urllib.request.Request(
            "https://remotive.com/api/remote-jobs?category=data&limit=20",
            headers={"User-Agent": "JobSearchBot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
            for item in data.get("jobs", [])[:20]:
                title = item.get("title", "")
                company = item.get("company_name", "")
                url = item.get("url", "")
                date = item.get("publication_date", "")
                tags = " ".join(item.get("tags", []))
                
                search_text = f"{title} {company} {tags}".lower()
                if any(kw in search_text for kw in KEYWORDS):
                    jobs.append({
                        "title": f"{title} at {company}",
                        "link": url,
                        "source": "Remotive",
                        "date": date[:10] if date else ""
                    })
    except Exception as e:
        print(f"  Remotive error: {e}")
    return jobs


def fetch_hn_jobs():
    """Fetch from Hacker News job stories (free Firebase API)."""
    jobs = []
    try:
        req = urllib.request.Request(
            "https://hacker-news.firebaseio.com/v0/jobstories.json",
            headers={"User-Agent": "JobSearchBot/1.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            story_ids = json.loads(response.read())[:15]  # latest 15 job posts
        
        for story_id in story_ids:
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            req = urllib.request.Request(item_url, headers={"User-Agent": "JobSearchBot/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                item = json.loads(response.read())
            
            title = item.get("title", "")
            url = item.get("url", f"https://news.ycombinator.com/item?id={story_id}")
            
            search_text = title.lower()
            if any(kw in search_text for kw in KEYWORDS):
                jobs.append({
                    "title": title,
                    "link": url,
                    "source": "Hacker News",
                    "date": ""
                })
    except Exception as e:
        print(f"  HN error: {e}")
    return jobs


def format_email(all_jobs):
    """Format jobs as HTML email."""
    if not all_jobs:
        return None
    
    # Deduplicate by link
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        if j["link"] not in seen:
            seen.add(j["link"])
            unique_jobs.append(j)
    
    if not unique_jobs:
        return None
    
    today = datetime.now().strftime("%B %d, %Y")
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 16px;">
        <h2 style="color: #1a56db; margin-bottom: 4px;">Daily Data Engineer Jobs - {today}</h2>
        <p style="color: #666; margin-top: 0;">Found {len(unique_jobs)} relevant job(s) matching: Snowflake, Databricks, dbt, Python, AWS</p>
        <hr style="border: 1px solid #e5e7eb;">
    """
    
    for i, job in enumerate(unique_jobs, 1):
        source_color = {"RemoteOK": "#059669", "Remotive": "#7c3aed", "Hacker News": "#f59e0b"}.get(job["source"], "#6b7280")
        html += f"""
        <div style="margin: 14px 0; padding: 12px; border-left: 3px solid #1a56db; background: #f9fafb;">
            <h3 style="margin: 0 0 4px 0; font-size: 1em;">
                <a href="{job['link']}" style="color: #1a56db; text-decoration: none;">{i}. {job['title']}</a>
            </h3>
            <span style="background: {source_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75em;">{job['source']}</span>
            {f'<span style="color: #6b7280; font-size: 0.8em; margin-left: 8px;">{job["date"]}</span>' if job["date"] else ''}
            <br><a href="{job['link']}" style="color: #1a56db; font-size: 0.85em; margin-top: 6px; display: inline-block;">Apply Now &rarr;</a>
        </div>
        """
    
    html += """
        <hr style="border: 1px solid #e5e7eb;">
        <p style="color: #999; font-size: 0.8em;">
            Automated by Daily DE Automation | Sources: RemoteOK, Remotive, Hacker News<br>
            Keywords: data engineer, snowflake, databricks, dbt, spark, airflow, python, aws
        </p>
    </body>
    </html>
    """
    return html


def send_email(subject, html_body):
    """Send email via Gmail SMTP."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())
    
    print(f"Email sent to {EMAIL_TO}")


def main():
    print(f"Job search started at {datetime.now()}")
    
    all_jobs = []
    
    print("Fetching RemoteOK...")
    all_jobs.extend(fetch_remoteok_jobs())
    print(f"  Found {len(all_jobs)} jobs so far")
    
    print("Fetching Remotive...")
    remotive = fetch_remotive_jobs()
    all_jobs.extend(remotive)
    print(f"  Found {len(remotive)} from Remotive")
    
    print("Fetching Hacker News...")
    hn = fetch_hn_jobs()
    all_jobs.extend(hn)
    print(f"  Found {len(hn)} from HN")
    
    print(f"\nTotal matching jobs: {len(all_jobs)}")
    
    if all_jobs:
        html = format_email(all_jobs)
        if html:
            today = datetime.now().strftime("%b %d")
            subject = f"[Jobs] {len(all_jobs)} DE jobs found - {today}"
            send_email(subject, html)
            print("Email sent!")
        else:
            print("No jobs after deduplication.")
    else:
        print("No matching jobs found today. No email sent.")


if __name__ == "__main__":
    main()

import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import urllib.request
import urllib.parse

# Configuration from environment/secrets
API_KEY = os.environ.get("GOOGLE_CSE_API_KEY")
CSE_ID = os.environ.get("GOOGLE_CSE_ID")
EMAIL_TO = os.environ.get("EMAIL_TO", "ranga.k565@gmail.com")
GMAIL_USER = os.environ.get("EMAIL_TO", "ranga.k565@gmail.com")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

# Load search keywords
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, "keywords.json")) as f:
    config = json.load(f)

SEARCH_QUERIES = config["queries"]
EXCLUDE_COMPANIES = config.get("exclude_companies", [])


def search_google_jobs(query, num_results=5):
    """Search Google Custom Search API for job listings."""
    params = urllib.parse.urlencode({
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "num": num_results,
        "dateRestrict": "d1",  # last 1 day
        "sort": "date"
    })
    url = f"https://www.googleapis.com/customsearch/v1?{params}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            return data.get("items", [])
    except Exception as e:
        print(f"Error searching '{query}': {e}")
        return []


def format_results(all_results):
    """Format job results into HTML email."""
    if not all_results:
        return None
    
    # Deduplicate by link
    seen = set()
    unique_results = []
    for r in all_results:
        if r["link"] not in seen:
            seen.add(r["link"])
            unique_results.append(r)
    
    # Filter out excluded companies
    filtered = []
    for r in unique_results:
        title_lower = r.get("title", "").lower()
        if not any(exc.lower() in title_lower for exc in EXCLUDE_COMPANIES):
            filtered.append(r)
    
    if not filtered:
        return None
    
    today = datetime.now().strftime("%B %d, %Y")
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto;">
        <h2 style="color: #1a56db;">Daily Job Alerts - {today}</h2>
        <p style="color: #666;">Found {len(filtered)} new job(s) matching your profile.</p>
        <hr style="border: 1px solid #e5e7eb;">
    """
    
    for i, result in enumerate(filtered, 1):
        title = result.get("title", "No title")
        link = result.get("link", "#")
        snippet = result.get("snippet", "")
        source = result.get("displayLink", "")
        
        html += f"""
        <div style="margin: 16px 0; padding: 12px; border-left: 3px solid #1a56db; background: #f9fafb;">
            <h3 style="margin: 0 0 4px 0;">
                <a href="{link}" style="color: #1a56db; text-decoration: none;">{i}. {title}</a>
            </h3>
            <p style="margin: 4px 0; color: #666; font-size: 0.85em;">{source}</p>
            <p style="margin: 4px 0; font-size: 0.9em;">{snippet}</p>
            <a href="{link}" style="color: #1a56db; font-weight: bold; font-size: 0.9em;">Apply Now &rarr;</a>
        </div>
        """
    
    html += """
        <hr style="border: 1px solid #e5e7eb;">
        <p style="color: #999; font-size: 0.8em;">
            Automated job search by Daily DE Automation.<br>
            Keywords: Senior Data Engineer, Snowflake, Databricks, dbt, AWS
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
    
    all_results = []
    for query in SEARCH_QUERIES:
        print(f"Searching: {query}")
        results = search_google_jobs(query, num_results=5)
        all_results.extend(results)
        print(f"  Found {len(results)} results")
    
    print(f"\nTotal results: {len(all_results)}")
    
    html = format_results(all_results)
    
    if html:
        today = datetime.now().strftime("%b %d")
        subject = f"[Jobs] {len(set(r['link'] for r in all_results))} new DE jobs - {today}"
        send_email(subject, html)
        print("Email sent successfully!")
    else:
        print("No new jobs found today.")


if __name__ == "__main__":
    main()

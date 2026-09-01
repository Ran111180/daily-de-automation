import json
import os
import random
from datetime import datetime
import urllib.request

LINKEDIN_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
PERSON_URN = os.environ.get("LINKEDIN_PERSON_URN", "urn:li:person:PFESNi6jid")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOPICS_FILE = os.path.join(SCRIPT_DIR, "topics.json")


def load_topics():
    with open(TOPICS_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_todays_topic(topics):
    """Pick today's topic based on day of year (cycles through all topics)."""
    day_of_year = datetime.now().timetuple().tm_yday
    index = day_of_year % len(topics)
    return topics[index]


def post_to_linkedin(text):
    """Post text content to LinkedIn."""
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    payload = json.dumps({
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }).encode("utf-8")
    
    headers = {
        "Authorization": f"Bearer {LINKEDIN_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202401"
    }
    
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            print(f"Posted successfully! ID: {result.get('id')}")
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"Error posting: {e.code} - {error_body}")
        return None


def main():
    topics = load_topics()
    
    # Allow posting a specific topic by title via env var
    specific_title = os.environ.get("POST_SPECIFIC_TOPIC")
    if specific_title:
        topic = next((t for t in topics if specific_title.lower() in t['title'].lower()), None)
        if not topic:
            print(f"Topic '{specific_title}' not found. Available: {[t['title'] for t in topics]}")
            return
    else:
        topic = get_todays_topic(topics)
    
    print(f"Today's topic: {topic['title']}")
    print(f"Content length: {len(topic['content'])} chars")
    print("---")
    print(topic["content"][:200] + "...")
    print("---")
    
    result = post_to_linkedin(topic["content"])
    
    if result:
        print(f"\nPosted to LinkedIn at {datetime.now()}")
    else:
        print("\nFailed to post. Check token validity.")


if __name__ == "__main__":
    main()

import os
import json
import time
import schedule
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
from datetime import datetime
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import pandas as pd
from typing import List, Dict, Optional
import re
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

class ConferenceTracker:
    def __init__(self):
        self.conferences_file = "conferences.json"
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.conferences = self._load_conferences()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def _load_conferences(self) -> List[Dict]:
        """Load conferences from JSON file."""
        if os.path.exists(self.conferences_file):
            with open(self.conferences_file, 'r') as f:
                return json.load(f)
        return []

    def _save_conferences(self):
        """Save conferences to JSON file."""
        with open(self.conferences_file, 'w') as f:
            json.dump(self.conferences, f, indent=2)

    def add_conference(self, name: str, year: int, keywords: List[str], link: Optional[str] = None):
        """Add a new conference to track."""
        conference = {
            "name": name,
            "year": year,
            "keywords": keywords,
            "link": link,
            "last_checked": datetime.now().isoformat()
        }
        self.conferences.append(conference)
        self._save_conferences()

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts using sentence transformers."""
        embedding1 = self.model.encode(text1, convert_to_tensor=True)
        embedding2 = self.model.encode(text2, convert_to_tensor=True)
        similarity = embedding1 @ embedding2.T
        return float(similarity[0][0])

    def _search_google(self, query: str) -> List[Dict]:
        """Search Google for conference information."""
        results = []
        encoded_query = quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        
        try:
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for search results
            for result in soup.select('div.g'):
                title_elem = result.select_one('h3')
                link_elem = result.select_one('a')
                snippet_elem = result.select_one('div.VwiC3b')
                
                if title_elem and link_elem:
                    results.append({
                        'title': title_elem.get_text(),
                        'link': link_elem.get('href'),
                        'snippet': snippet_elem.get_text() if snippet_elem else '',
                        'source': 'Google Search'
                    })
        except Exception as e:
            print(f"Error searching Google: {e}")
        
        return results

    def _search_conference_websites(self, conference: Dict) -> List[Dict]:
        """Search common conference websites."""
        results = []
        next_year = conference['year'] + 1
        
        # List of common conference websites to check
        websites = [
            f"https://www.call4papers.com/search?q={quote_plus(conference['name'])}",
            f"https://www.wikicfp.com/cfp/search?q={quote_plus(conference['name'])}"
        ]
        
        for url in websites:
            try:
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract conference information based on website structure
                for link in soup.find_all('a', href=True):
                    if any(keyword.lower() in link.text.lower() for keyword in conference['keywords']):
                        results.append({
                            'title': link.text,
                            'link': link['href'],
                            'source': url
                        })
            except Exception as e:
                print(f"Error searching {url}: {e}")
        
        return results

    def _search_conference(self, conference: Dict) -> List[Dict]:
        """Search for conference information using multiple sources."""
        results = []
        
        # Search query construction with year and keywords
        search_query = f"{conference['name']} conference {conference['year'] + 1} {' '.join(conference['keywords'])}"
        
        # Search Google
        google_results = self._search_google(search_query)
        results.extend(google_results)
        
        # Search conference websites
        website_results = self._search_conference_websites(conference)
        results.extend(website_results)
        
        return results

    def _send_email_notification(self, conference: Dict, match: Dict):
        """Send email notification about a potential conference match."""
        try:
            msg = MIMEMultipart()
            msg['From'] = os.getenv('SMTP_USERNAME')
            msg['To'] = os.getenv('NOTIFICATION_EMAIL')
            msg['Subject'] = f"Potential Conference Match: {conference['name']}"
            
            body = f"""
            A potential match has been found for the conference you're tracking:
            
            Original Conference: {conference['name']} ({conference['year']})
            Found Match: {match['title']}
            Source: {match['source']}
            Link: {match['link']}
            
            Similarity Score: {self._calculate_similarity(conference['name'], match['title']):.2f}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT')))
            server.starttls()
            server.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg)
            server.quit()
            
            print(f"Email notification sent for {conference['name']}")
        except Exception as e:
            print(f"Error sending email notification: {e}")

    def check_conferences(self):
        """Check all conferences for updates."""
        for conference in self.conferences:
            print(f"Checking conference: {conference['name']}")
            results = self._search_conference(conference)
            
            for result in results:
                similarity = self._calculate_similarity(
                    conference['name'],
                    result['title']
                )
                
                if similarity > float(os.getenv('SIMILARITY_THRESHOLD', 0.7)):
                    print(f"Potential match found for {conference['name']}")
                    self._send_email_notification(conference, result)
                    
            conference['last_checked'] = datetime.now().isoformat()
        
        self._save_conferences()

def main():
    tracker = ConferenceTracker()
    
    # Schedule weekly checks
    schedule.every().monday.at("00:00").do(tracker.check_conferences)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 
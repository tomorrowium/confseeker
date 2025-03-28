from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import schedule
import time
import threading
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import pandas as pd
from dateutil import parser
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# Azure SQL Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///conferences.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Conference model
class Conference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    keywords = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500))
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Idle')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'year': self.year,
            'keywords': self.keywords.split(','),
            'link': self.link,
            'last_checked': self.last_checked.isoformat(),
            'status': self.status
        }

# Create tables
with app.app_context():
    db.create_all()

def _calculate_similarity(text1, text2):
    """Calculate semantic similarity between two texts."""
    embeddings = model.encode([text1, text2])
    similarity = float(pd.DataFrame(embeddings).corr().iloc[0, 1])
    return similarity

def _search_conference(conference):
    """Search for conference updates using Google."""
    search_query = f"{conference['name']} {conference['year'] + 1} conference"
    url = f"https://www.google.com/search?q={search_query}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for result in soup.find_all('div', class_='g'):
            title_elem = result.find('h3')
            link_elem = result.find('a')
            if title_elem and link_elem:
                results.append({
                    'title': title_elem.text,
                    'link': link_elem['href'],
                    'source': 'Google Search'
                })
        
        return results[:5]  # Return top 5 results
    except Exception as e:
        print(f"Error searching for conference: {e}")
        return []

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Start the scheduler in a background thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

@app.route('/api/conferences', methods=['GET'])
def get_conferences():
    conferences = Conference.query.all()
    return jsonify([conf.to_dict() for conf in conferences])

@app.route('/api/conferences', methods=['POST'])
def add_conference():
    data = request.json
    keywords_str = ','.join(data['keywords'])
    
    conference = Conference(
        name=data['name'],
        year=data['year'],
        keywords=keywords_str,
        link=data.get('link')
    )
    
    db.session.add(conference)
    db.session.commit()
    
    return jsonify(conference.to_dict()), 201

@app.route('/api/conferences/<int:conference_id>', methods=['PUT'])
def update_conference(conference_id):
    conference = Conference.query.get_or_404(conference_id)
    data = request.json
    
    conference.name = data['name']
    conference.year = data['year']
    conference.keywords = ','.join(data['keywords'])
    conference.link = data.get('link')
    
    db.session.commit()
    return jsonify(conference.to_dict())

@app.route('/api/conferences/<int:conference_id>', methods=['DELETE'])
def delete_conference(conference_id):
    conference = Conference.query.get_or_404(conference_id)
    db.session.delete(conference)
    db.session.commit()
    return '', 204

@app.route('/api/conferences/check', methods=['POST'])
def check_conferences():
    conferences = Conference.query.all()
    results = []
    
    for conf in conferences:
        conf.status = 'Checking...'
        db.session.commit()
        
        # Convert database model to search format
        search_conf = {
            'name': conf.name,
            'year': conf.year,
            'keywords': conf.keywords.split(','),
            'link': conf.link
        }
        
        # Search for updates
        search_results = _search_conference(search_conf)
        
        # Update status
        conf.status = 'Checked'
        conf.last_checked = datetime.utcnow()
        db.session.commit()
        
        # Add results
        for result in search_results:
            similarity = _calculate_similarity(conf.name, result['title'])
            if similarity > float(os.getenv('SIMILARITY_THRESHOLD', 0.7)):
                results.append({
                    'conference_id': conf.id,
                    'conference_name': conf.name,
                    'title': result['title'],
                    'source': result['source'],
                    'link': result['link'],
                    'similarity': similarity
                })
    
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Use Azure's PORT environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 
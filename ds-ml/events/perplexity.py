import os
import csv
from datetime import datetime, timedelta
from openai import OpenAI

PERPLEXITY_API_KEY = ""

import csv
from datetime import datetime, timedelta
from openai import OpenAI


class EventScraper:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
    
    def get_events(self, location, days_back=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = f"""Events in {location} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}.
        Format: Event Name | Type | Date (YYYY-MM-DD) | Time | Venue | Area | Description | Price
        List each event on a new line."""
        
        response = self.client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "user", "content": query}
            ],
            max_tokens=3000,
            temperature=0.3
        )
        
        return response.choices[0].message.content
    
    def parse_events(self, raw_data):
        events = []
        for line in raw_data.strip().split('\n'):
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 7:
                    events.append({
                        'name': parts[0],
                        'type': parts[1],
                        'date': self.normalize_date(parts[2]),
                        'time': parts[3],
                        'venue': parts[4],
                        'location': parts[5],
                        'description': parts[6],
                        'price': parts[7] if len(parts) > 7 else 'N/A'
                    })
        return events
    
    def normalize_date(self, date_str):
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%B %d, %Y', '%d %B %Y']:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except:
                continue
        return date_str
    
    def export_csv(self, events, filename):
        if events:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'type', 'date', 'time', 'venue', 'location', 'description', 'price'])
                writer.writeheader()
                writer.writerows(events)


def fetch_events(location, days_back, output_file):
    api_key = PERPLEXITY_API_KEY or os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise ValueError("No API key found. Set PERPLEXITY_API_KEY variable at top of file or as environment variable")
    
    scraper = EventScraper(api_key)
    raw_data = scraper.get_events(location, days_back)
    events = scraper.parse_events(raw_data)
    scraper.export_csv(events, output_file)
    return events


if __name__ == "__main__":
    events = fetch_events("Dublin, Ireland", 14, "dublin_events.csv")
import os
import csv
from datetime import datetime, timedelta
from openai import OpenAI

PERPLEXITY_API_KEY = ""


class EventScraper:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
    
    def get_events(self, location, days_back=7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        date_range_str = f"{start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}"
        
        venues = [
            "3Arena", "Olympia Theatre", "Vicar Street", "Whelan's", 
            "Academy", "Button Factory", "National Stadium", "Aviva Stadium",
            "Croke Park", "RDS", "Convention Centre", "Bord Gais Theatre"
        ]
        
        query = f"""Search for ALL events in {location} between {date_range_str}.

Check each major venue: {', '.join(venues)}

Include:
- All concerts and music performances
- All sports matches (GAA, rugby, football, etc)
- All festivals and cultural events  
- All theatre and comedy shows
- All conferences and exhibitions
- Marathons and races

Search each day individually from {start_date.strftime('%B %d')} through {end_date.strftime('%B %d, %Y')}.

Output format (no headers, no bullets):
Event Name | Event Type | YYYY-MM-DD | Time | Venue Name | Area | Description | Price

One event per line. Be exhaustive and include everything."""
        
        response = self.client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "user", "content": query}
            ],
            max_tokens=5000,
            temperature=0.1
        )
        
        main_results = response.choices[0].message.content
        
        extra_query = f"""Find any additional concerts, gigs, shows, or events in {location} between {date_range_str} that weren't mentioned yet. Check smaller venues, pubs with live music, club nights, markets, etc. Same format."""
        
        extra_response = self.client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "user", "content": extra_query}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        return main_results + "\n" + extra_response.choices[0].message.content
    
    def parse_events(self, raw_data):
        events = []
        seen = set()
        
        for line in raw_data.strip().split('\n'):
            line = line.strip()
            
            for prefix in ['-', '*', '•', '>', '–', '+']:
                if line.startswith(prefix):
                    line = line[len(prefix):].strip()
            
            if not line or len(line) < 10:
                continue
            
            if any(skip in line.lower() for skip in ['event name', '---', '===', '***', 'format:', 'output:']):
                continue
                
            if '|' in line and line.count('|') >= 6:
                parts = [p.strip() for p in line.split('|')]
                
                if len(parts) >= 7:
                    name = parts[0].strip().lstrip(',').strip('"').strip()
                    
                    if not name or len(name) < 2:
                        continue
                    
                    date_str = self.normalize_date(parts[2])
                    venue = parts[4].strip()
                    
                    event_key = f"{name.lower()}_{date_str}_{venue.lower()}"
                    
                    if event_key not in seen:
                        seen.add(event_key)
                        events.append({
                            'name': name,
                            'type': parts[1].strip(),
                            'date': date_str,
                            'time': parts[3].strip() or 'TBA',
                            'venue': venue,
                            'location': parts[5].strip() or location,
                            'description': parts[6].strip().strip('"'),
                            'price': parts[7].strip() if len(parts) > 7 else 'TBA'
                        })
        
        return events
    
    def normalize_date(self, date_str):
        date_str = str(date_str).strip()
        
        for separator in [' to ', '–', ' - ', '—', ' until ', ' through ']:
            if separator in date_str:
                date_str = date_str.split(separator)[0].strip()
                break
        
        months = {
            'January': 'Jan', 'February': 'Feb', 'March': 'Mar',
            'April': 'Apr', 'May': 'May', 'June': 'Jun',
            'July': 'Jul', 'August': 'Aug', 'September': 'Sep',
            'October': 'Oct', 'November': 'Nov', 'December': 'Dec'
        }
        
        for full, short in months.items():
            date_str = date_str.replace(full, short)
        
        date_str = date_str.replace('st,', '').replace('nd,', '').replace('rd,', '').replace('th,', '')
        date_str = date_str.replace('st ', ' ').replace('nd ', ' ').replace('rd ', ' ').replace('th ', ' ')
        
        current_year = datetime.now().year
        
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
            '%Y/%m/%d',
            '%b %d',
            '%B %d'
        ]
        
        for fmt in formats:
            try:
                if fmt in ['%b %d', '%B %d']:
                    date_str_with_year = f"{date_str}, {current_year}"
                    dt = datetime.strptime(date_str_with_year, f"{fmt}, %Y")
                else:
                    dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
        
        return date_str
    
    def export_csv(self, events, filename):
        if events:
            events.sort(key=lambda x: (x['date'], x['venue'], x['name']))
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
    
    valid_events = []
    for event in events:
        if event['name'] and len(event['name']) > 1:
            valid_events.append(event)
    
    scraper.export_csv(valid_events, output_file)
    return valid_events


if __name__ == "__main__":
    events = fetch_events("Dublin, Ireland", 14, "dublin_events.csv")
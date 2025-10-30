

import csv
import json
import requests
from datetime import datetime
import time

# Known Irish teams with their sportsdbids
IRISH_TEAMS = {
    'Shamrock Rovers': '133978',
    'Bohemians': '134043',
    'St Patricks': '134792',
    'Shelbourne': '138033',
    'Dundalk': '134618',
    'Cork City': '138031',
    'Leinster': '135599',
    'Munster': '135601'
}

def get_fixtures():
    """Get fixtures for all Irish teams"""
    api_key = '3' 
    all_fixtures = []
    
    print("Getting fixtures for Irish teams...")
    print("="*50)
    
    for team_name, team_id in IRISH_TEAMS.items():
        print(f"\n{team_name}:")
        
        # Get next events
        url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsnext.php"
        params = {'id': team_id}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data and 'events' in data and data['events']:
                    for event in data['events']:
                        fixture = {
                            'event_name': event.get('strEvent', ''),
                            'date': event.get('dateEvent', ''),
                            'time': event.get('strTime', '').split('+')[0] if event.get('strTime') else 'TBD',
                            'venue': event.get('strVenue', ''),
                            'home_team': event.get('strHomeTeam', ''),
                            'away_team': event.get('strAwayTeam', ''),
                            'sport': event.get('strSport', ''),
                            'league': event.get('strLeague', ''),
                            'source': 'TheSportsDB'
                        }
                        all_fixtures.append(fixture)
                        print(f"  {fixture['date']}: {fixture['event_name']}")
                else:
                    print(f"  No upcoming fixtures")
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(0.5)
    
    return all_fixtures

def save_data(fixtures):
    """Save fixtures to CSV and JSON"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save CSV
    csv_file = f'dublin_sports_{timestamp}.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if fixtures:
            writer = csv.DictWriter(f, fieldnames=fixtures[0].keys())
            writer.writeheader()
            writer.writerows(fixtures)
    
    # Save JSON
    json_file = f'dublin_sports_{timestamp}.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, indent=2)
    
    print(f"\nSaved {len(fixtures)} events to:")
    print(f"  - {csv_file}")
    print(f"  - {json_file}")
    
    return csv_file, json_file

def main():
    print("\n" + "="*50)
    print("IRISH SPORTS FIXTURES - REAL DATA ONLY")
    print("="*50 + "\n")
    
    fixtures = get_fixtures()
    
    if fixtures:
        save_data(fixtures)
        
        # Show summary
        print("\nSummary:")
        sports = {}
        for f in fixtures:
            sport = f.get('sport', 'Unknown')
            sports[sport] = sports.get(sport, 0) + 1
        
        for sport, count in sports.items():
            print(f"  {sport}: {count} events")
    else:
        print("\nNo fixtures found!")

if __name__ == "__main__":
    main()
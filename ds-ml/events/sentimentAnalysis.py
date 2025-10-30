import csv
from openai import OpenAI
import json
import os

PERPLEXITY_API_KEY = ""


class DemandAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
    
    def analyze_impact(self, events):
        events_text = "\n".join([
            f"{i+1}. {e['name']} | {e['type']} | {e['date']} | {e['venue']} | {e.get('description', '')[:100]}"
            for i, e in enumerate(events)
        ])
        
        query = f"""Rate each Dublin event's impact on hotel demand from 1-10:
        1-3: Local event, minimal tourism
        4-6: Regional draw, moderate bookings  
        7-9: Major event, significant tourism
        10: International event, hotels full
        
        Events:
        {events_text}
        
        Return ONLY numbers separated by commas. Example: 7,3,5,8,4"""
        
        response = self.client.chat.completions.create(
            model="sonar-pro",
            messages=[{"role": "user", "content": query}],
            max_tokens=500,
            temperature=0.3
        )
        
        try:
            scores_text = response.choices[0].message.content.strip()
            scores_text = scores_text.replace('[', '').replace(']', '').replace(' ', '')
            scores = [int(x) for x in scores_text.split(',')]
            if len(scores) != len(events):
                return [5] * len(events)
            return scores
        except:
            return [5] * len(events)
    
    def process_csv(self, input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            events = list(reader)
        
        if not events:
            return
        
        batch_size = 8
        all_scores = []
        
        for i in range(0, len(events), batch_size):
            batch = events[i:i+batch_size]
            scores = self.analyze_impact(batch)
            all_scores.extend(scores)
        
        for event, score in zip(events, all_scores):
            event['impact_score'] = score
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = list(events[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(events)
        
        return events


def analyze_hotel_demand(input_csv="dublin_events.csv", output_csv="dublin_events_analyzed.csv"):
    api_key = PERPLEXITY_API_KEY or os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        raise ValueError("No API key found. Set PERPLEXITY_API_KEY at top of file")
    
    analyzer = DemandAnalyzer(api_key)
    return analyzer.process_csv(input_csv, output_csv)


if __name__ == "__main__":
    analyze_hotel_demand()
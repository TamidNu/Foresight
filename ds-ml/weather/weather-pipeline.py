import pandas as pd
import requests
from datetime import datetime, timedelta

def fetch_dublin_weather(start_date='2023-01-01', end_date=None):
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': 53.3498,
        'longitude': -6.2603,
        'start_date': start_date,
        'end_date': end_date,
        'daily': [
            'temperature_2m_max',
            'temperature_2m_min', 
            'temperature_2m_mean',
            'precipitation_sum',
            'rain_sum',
            'wind_speed_10m_max',
            'weather_code'
        ],
        'timezone': 'Europe/Dublin'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    daily_data = data['daily']
    weather_df = pd.DataFrame({
        'date': pd.to_datetime(daily_data['time']),
        'temp_max': daily_data['temperature_2m_max'],
        'temp_min': daily_data['temperature_2m_min'],
        'temp_mean': daily_data['temperature_2m_mean'],
        'precipitation': daily_data['precipitation_sum'],
        'rain': daily_data['rain_sum'],
        'wind_max': daily_data['wind_speed_10m_max'],
        'weather_code': daily_data['weather_code']
    })
    
    return weather_df

def fetch_irish_holidays(start_year=2023, end_year=None):
    if end_year is None:
        end_year = datetime.now().year
    
    holidays_list = []
    
    for year in range(start_year, end_year + 1):
        url = f"https://date.nager.at/api/v3/publicholidays/{year}/IE"
        response = requests.get(url)
        public_holidays = response.json()
        
        for holiday in public_holidays:
            holidays_list.append({
                'date': pd.to_datetime(holiday['date']),
                'name': holiday['localName'],
                'type': 'public_holiday'
            })
        
        school_holidays = [
            {'name': 'February Mid-term', 'start': f'{year}-02-13', 'end': f'{year}-02-17'},
            {'name': 'Easter Holidays', 'start': f'{year}-04-01', 'end': f'{year}-04-14'},
            {'name': 'Summer Holidays', 'start': f'{year}-07-01', 'end': f'{year}-08-31'},
            {'name': 'October Mid-term', 'start': f'{year}-10-28', 'end': f'{year}-11-01'},
            {'name': 'Christmas Holidays', 'start': f'{year}-12-22', 'end': f'{year+1}-01-05' if year < end_year else f'{year}-12-31'}
        ]
        
        for holiday_period in school_holidays:
            start = pd.to_datetime(holiday_period['start'])
            end = pd.to_datetime(holiday_period['end'])
            date_range = pd.date_range(start, end)
            
            for date in date_range:
                if date <= datetime.now():
                    holidays_list.append({
                        'date': date,
                        'name': holiday_period['name'],
                        'type': 'school_holiday'
                    })
    
    holidays_df = pd.DataFrame(holidays_list)
    if not holidays_df.empty:
        holidays_df = holidays_df.drop_duplicates(subset=['date'])
        holidays_df = holidays_df.sort_values('date')
    
    return holidays_df

def main(start_date='2023-01-01', end_date=None):
    weather_df = fetch_dublin_weather(start_date, end_date)
    weather_df.to_csv('dublin_weather.csv', index=False)
    print(f"Weather data saved: {len(weather_df)} days")
    print(f"Date range: {weather_df['date'].min().date()} to {weather_df['date'].max().date()}")
    
    start_year = pd.to_datetime(start_date).year
    end_year = pd.to_datetime(end_date).year if end_date else datetime.now().year
    
    holidays_df = fetch_irish_holidays(start_year, end_year)
    holidays_df.to_csv('irish_holidays.csv', index=False)
    print(f"Holiday data saved: {len(holidays_df)} days")
    
    return weather_df, holidays_df

if __name__ == "__main__":
    weather, holidays = main()
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def fetch_dublin_weather_2023():
    """Fetch Dublin weather data for year 2023"""
    
    dublin_lat = 53.3498
    dublin_lon = -6.2603
    
    start_date = '2023-01-01'
    end_date = '2023-12-31'
    
    print(f"Fetching Dublin weather data for 2023...")
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        'latitude': dublin_lat,
        'longitude': dublin_lon,
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
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Create DataFrame
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
        
        # Add month and season
        weather_df['month'] = weather_df['date'].dt.month
        weather_df['month_name'] = weather_df['date'].dt.strftime('%B')
        
        # Define seasons
        def get_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Autumn'
        
        weather_df['season'] = weather_df['month'].apply(get_season)
        
        print(f"Successfully fetched {len(weather_df)} days of weather data for 2023")
        return weather_df
        
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def create_weather_graphs(weather_df):
    """Create three separate weather visualizations"""
    
    # Graph 1: Daily Temperature Range
    plt.figure(figsize=(16, 6))
    
    plt.fill_between(weather_df['date'], weather_df['temp_min'], weather_df['temp_max'], 
                     alpha=0.3, color='orange', label='Daily Temperature Range')
    plt.plot(weather_df['date'], weather_df['temp_mean'], 
             color='red', linewidth=1.5, label='Daily Mean Temperature')
    
    # Add 30-day rolling average
    rolling_mean = weather_df['temp_mean'].rolling(window=30, center=True).mean()
    plt.plot(weather_df['date'], rolling_mean, 
             color='darkred', linewidth=2.5, label='30-Day Average', linestyle='--')
    
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.title('Dublin Daily Temperature Variation - 2023', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # Add season backgrounds with labels
    season_colors = {'Winter': 'lightblue', 'Spring': 'lightgreen', 
                    'Summer': 'lightyellow', 'Autumn': 'peachpuff'}
    
    for season in ['Winter', 'Spring', 'Summer', 'Autumn']:
        season_data = weather_df[weather_df['season'] == season]
        if len(season_data) > 0:
            plt.axvspan(season_data['date'].min(), season_data['date'].max(), 
                       alpha=0.15, color=season_colors[season])
            # Add season label
            mid_date = season_data['date'].min() + (season_data['date'].max() - season_data['date'].min()) / 2
            plt.text(mid_date, plt.ylim()[1] * 0.95, season, 
                    horizontalalignment='center', fontsize=10, 
                    style='italic', color='gray')
    
    plt.tight_layout()
    plt.show()
    
    # Graph 2: Monthly Average Temperature
    plt.figure(figsize=(14, 7))
    
    monthly_stats = weather_df.groupby('month_name').agg({
        'temp_mean': 'mean',
        'temp_max': 'mean',
        'temp_min': 'mean'
    }).reindex(['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December'])
    
    x_pos = np.arange(len(monthly_stats))
    width = 0.25
    
    bars1 = plt.bar(x_pos - width, monthly_stats['temp_min'], width, 
                    label='Average Minimum', color='skyblue', edgecolor='navy', linewidth=1)
    bars2 = plt.bar(x_pos, monthly_stats['temp_mean'], width, 
                    label='Average Mean', color='orange', edgecolor='darkorange', linewidth=1)
    bars3 = plt.bar(x_pos + width, monthly_stats['temp_max'], width, 
                    label='Average Maximum', color='coral', edgecolor='darkred', linewidth=1)
    
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Temperature (°C)', fontsize=12)
    plt.title('Dublin Average Monthly Temperatures - 2023', fontsize=14, fontweight='bold')
    plt.xticks(x_pos, monthly_stats.index, rotation=0)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}°', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    # Graph 3: Average Monthly Precipitation
    plt.figure(figsize=(14, 7))
    
    monthly_precip = weather_df.groupby('month_name')['precipitation'].mean().reindex(
        ['January', 'February', 'March', 'April', 'May', 'June', 
         'July', 'August', 'September', 'October', 'November', 'December'])
    
    # Line plot for average daily precipitation
    plt.plot(range(len(monthly_precip)), monthly_precip, 
             color='steelblue', marker='o', linewidth=2.5, 
             markersize=10, markerfacecolor='lightblue',
             markeredgewidth=2, markeredgecolor='navy')
    
    # Add value labels on each point
    for i, value in enumerate(monthly_precip):
        plt.text(i, value + 0.1, f'{value:.1f}mm', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add overall average line
    avg_precip = monthly_precip.mean()
    plt.axhline(y=avg_precip, color='red', linestyle='--', 
               alpha=0.6, linewidth=2, label=f'Year Average: {avg_precip:.1f}mm')
    
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Average Daily Precipitation (mm)', fontsize=12)
    plt.title('Dublin Average Daily Precipitation by Month - 2023', fontsize=14, fontweight='bold')
    plt.xticks(range(len(monthly_precip)), monthly_precip.index, rotation=0)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, max(monthly_precip) * 1.2)  # Add some space at the top
    
    plt.tight_layout()
    plt.show()

    # Graph 4: Daily Precipitation
    plt.figure(figsize=(16, 6))
    
    # Bar plot for daily precipitation
    plt.bar(weather_df['date'], weather_df['precipitation'], 
            color='steelblue', alpha=0.6, width=1, edgecolor='none')
    
    # Add 30-day rolling average
    rolling_precip_30 = weather_df['precipitation'].rolling(window=30, center=True).mean()
    plt.plot(weather_df['date'], rolling_precip_30, 
             color='darkblue', linewidth=2.5, label='30-Day Average')
    
    plt.ylabel('Precipitation (mm)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.title('Dublin Daily Precipitation - 2023', fontsize=14, fontweight='bold')
    plt.legend(loc='upper right', fontsize=11)
    plt.grid(True, alpha=0.3)
    
    # Add season backgrounds with labels (very light)
    season_colors = {'Winter': 'lightblue', 'Spring': 'lightgreen', 
                    'Summer': 'lightyellow', 'Autumn': 'peachpuff'}
    
    for season in ['Winter', 'Spring', 'Summer', 'Autumn']:
        season_data = weather_df[weather_df['season'] == season]
        if len(season_data) > 0:
            plt.axvspan(season_data['date'].min(), season_data['date'].max(), 
                       alpha=0.1, color=season_colors[season])
            # Add season label at the top
            mid_date = season_data['date'].min() + (season_data['date'].max() - season_data['date'].min()) / 2
            plt.text(mid_date, plt.ylim()[1] * 0.95, season, 
                    horizontalalignment='center', fontsize=10, 
                    style='italic', color='gray')
    
    plt.tight_layout()
    plt.show()
    
    return weather_df

# Main execution
def analyze_dublin_2023():
    """Main function to fetch and visualize Dublin weather for 2023"""
    
    # Fetch weather data for 2023
    weather_df = fetch_dublin_weather_2023()
    
    if weather_df is not None:
        # Create visualizations
        create_weather_graphs(weather_df)
        
        # Print summary statistics
        print("\n" + "="*60)
        print("DUBLIN 2023 WEATHER SUMMARY")
        print("="*60)
        
        print(f"\nTemperature Statistics:")
        print(f"  • Annual Average: {weather_df['temp_mean'].mean():.1f}°C")
        print(f"  • Warmest Day: {weather_df.loc[weather_df['temp_max'].idxmax(), 'date'].strftime('%B %d')} ({weather_df['temp_max'].max():.1f}°C)")
        print(f"  • Coldest Day: {weather_df.loc[weather_df['temp_min'].idxmin(), 'date'].strftime('%B %d')} ({weather_df['temp_min'].min():.1f}°C)")
        print(f"  • Temperature Range: {weather_df['temp_min'].min():.1f}°C to {weather_df['temp_max'].max():.1f}°C")
        
        print(f"\nPrecipitation Statistics:")
        print(f"  • Total Annual: {weather_df['precipitation'].sum():.0f}mm")
        print(f"  • Wettest Day: {weather_df.loc[weather_df['precipitation'].idxmax(), 'date'].strftime('%B %d')} ({weather_df['precipitation'].max():.1f}mm)")
        print(f"  • Rainy Days (>1mm): {(weather_df['precipitation'] > 1).sum()} days")
        print(f"  • Dry Days (0mm): {(weather_df['precipitation'] == 0).sum()} days")
        
        print(f"\nSeasonal Averages:")
        for season in ['Winter', 'Spring', 'Summer', 'Autumn']:
            season_avg = weather_df[weather_df['season'] == season]['temp_mean'].mean()
            print(f"  • {season}: {season_avg:.1f}°C")
        
        # Export data
        weather_df.to_csv('dublin_weather_2023.csv', index=False)
        print(f"\nWeather data exported to 'dublin_weather_2023.csv'")
        
        return weather_df
    
    return None

# Run the analysis
if __name__ == "__main__":
    weather_data = analyze_dublin_2023()
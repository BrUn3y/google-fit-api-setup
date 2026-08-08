#!/usr/bin/env python3
"""
Google Fit Widget Updater for GitHub Profile README
Updates fitness statistics in README.md with data from Google Fit API
"""

import json
import os
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def load_credentials():
    """Load credentials from token.json"""
    if not os.path.exists('token.json'):
        raise FileNotFoundError("token.json not found. Please run google_fit_setup.py first.")
    
    with open('token.json', 'r') as f:
        token_data = json.load(f)
    
    creds = Credentials(
        token=token_data['token'],
        refresh_token=token_data['refresh_token'],
        token_uri=token_data['token_uri'],
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        scopes=token_data['scopes']
    )
    
    return creds

def get_monthly_stats(service):
    """Get fitness statistics for the current month"""
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)
    
    start_time_millis = int(start_of_month.timestamp() * 1000)
    end_time_millis = int(now.timestamp() * 1000)
    
    # Data sources for different metrics
    data_sources = {
        'steps': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
        'calories': 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
        'distance': 'derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta',
        'active_minutes': 'derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes'
    }
    
    stats = {}
    
    for metric, data_source in data_sources.items():
        try:
            dataset = service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=data_source,
                datasetId=f'{start_time_millis}000000-{end_time_millis}000000'
            ).execute()
            
            total = 0
            if 'point' in dataset:
                for point in dataset['point']:
                    if 'value' in point and len(point['value']) > 0:
                        if 'intVal' in point['value'][0]:
                            total += point['value'][0]['intVal']
                        elif 'fpVal' in point['value'][0]:
                            total += point['value'][0]['fpVal']
            
            stats[metric] = total
        except Exception as e:
            print(f"Error fetching {metric}: {e}")
            stats[metric] = 0
    
    return stats

def format_number(num):
    """Format number with thousand separators"""
    return f"{int(num):,}"

def update_readme(stats):
    """Update README.md with new fitness statistics"""
    now = datetime.now()
    month_year = now.strftime("%B %Y")
    
    # Convert distance from meters to km
    distance_km = stats['distance'] / 1000
    
    fitness_section = f"""## 🏃 Fitness Stats ({month_year})

| 👟 Steps | 🔥 Calories | 📏 Distance | ⏱️ Active Minutes |
|----------|-------------|-------------|-------------------|
| {format_number(stats['steps'])} | {format_number(stats['calories'])} | {distance_km:.1f} km | {format_number(stats['active_minutes'])} |

*Updated automatically via Google Fit API*
"""
    
    # Read current README
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace fitness section
    start_marker = "## 🏃 Fitness Stats"
    end_marker = "*Updated automatically via Google Fit API*"
    
    start_idx = content.find(start_marker)
    if start_idx != -1:
        end_idx = content.find(end_marker, start_idx)
        if end_idx != -1:
            end_idx = content.find('\n', end_idx) + 1
            new_content = content[:start_idx] + fitness_section + content[end_idx:]
        else:
            new_content = content[:start_idx] + fitness_section
    else:
        # Append at the end if section doesn't exist
        new_content = content + "\n\n" + fitness_section
    
    # Write updated README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ README updated with fitness stats for {month_year}")
    print(f"   Steps: {format_number(stats['steps'])}")
    print(f"   Calories: {format_number(stats['calories'])}")
    print(f"   Distance: {distance_km:.1f} km")
    print(f"   Active Minutes: {format_number(stats['active_minutes'])}")

def main():
    """Main function"""
    try:
        # Load credentials
        creds = load_credentials()
        
        # Build Google Fit service
        service = build('fitness', 'v1', credentials=creds)
        
        # Get monthly statistics
        stats = get_monthly_stats(service)
        
        # Update README
        update_readme(stats)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == '__main__':
    main()

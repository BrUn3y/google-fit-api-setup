#!/usr/bin/env python3
"""
Google Fit API Setup Script

This script authenticates with Google Fit API using OAuth 2.0 and retrieves
your physical activity data including steps, calories, distance, and active minutes.
"""

import os
import datetime
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

# Load environment variables
load_dotenv()

# Required scopes for reading fitness data
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.body.read'
]

def create_credentials_file():
    """Creates credentials.json from environment variables"""
    client_id = os.getenv('GOOGLE_FIT_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_FIT_CLIENT_SECRET')

    if not client_id or not client_secret:
        raise ValueError("Missing GOOGLE_FIT_CLIENT_ID or GOOGLE_FIT_CLIENT_SECRET in .env")

    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost:8080/"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
    }

    with open('credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)

    return 'credentials.json'

def authenticate():
    """Handles OAuth 2.0 authentication flow"""
    creds = None

    # Check if token.json exists (previous authentication)
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("Starting OAuth 2.0 authentication flow...")
            credentials_file = create_credentials_file()
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("Authentication successful! Token saved to token.json")

    return creds

def get_fitness_data(service, days=7):
    """Retrieves fitness data for the specified number of days"""
    # Calculate time range (last N days)
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=days)

    # Convert to nanoseconds (Google Fit API format)
    start_time_ns = int(start_time.timestamp() * 1e9)
    end_time_ns = int(end_time.timestamp() * 1e9)

    print(f"\nFetching data from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")

    # Data sources to query
    data_sources = {
        'steps': 'derived:com.google.step_count.delta:com.google.android.gms:estimated_steps',
        'calories': 'derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended',
        'distance': 'derived:com.google.distance.delta:com.google.android.gms:merge_distance_delta',
        'active_minutes': 'derived:com.google.active_minutes:com.google.android.gms:merge_active_minutes'
    }

    results = {}

    for metric, data_source in data_sources.items():
        try:
            dataset_id = f"{start_time_ns}-{end_time_ns}"
            dataset = service.users().dataSources().datasets().get(
                userId='me',
                dataSourceId=data_source,
                datasetId=dataset_id
            ).execute()

            # Process data points
            total = 0
            if 'point' in dataset:
                for point in dataset['point']:
                    for value in point.get('value', []):
                        if 'intVal' in value:
                            total += value['intVal']
                        elif 'fpVal' in value:
                            total += value['fpVal']

            results[metric] = total
            print(f"✓ {metric.replace('_', ' ').title()}: {total:.2f}")

        except Exception as e:
            print(f"✗ Error fetching {metric}: {str(e)}")
            results[metric] = None

    return results

def main():
    """Main execution function"""
    print("=" * 50)
    print("Google Fit API - Activity Data Retrieval")
    print("=" * 50)

    try:
        # Authenticate
        creds = authenticate()

        # Build service
        print("\nConnecting to Google Fit API...")
        service = build('fitness', 'v1', credentials=creds)

        # Get fitness data
        data = get_fitness_data(service, days=7)

        print("\n" + "=" * 50)
        print("Summary (Last 7 days):")
        print("=" * 50)
        print(f"Steps: {data.get('steps', 0):.0f}")
        print(f"Calories: {data.get('calories', 0):.2f} kcal")
        print(f"Distance: {data.get('distance', 0):.2f} meters")
        print(f"Active Minutes: {data.get('active_minutes', 0):.0f} min")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())

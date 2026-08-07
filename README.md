# Google Fit API Setup

A Python script to authenticate with Google Fit API using OAuth 2.0 and retrieve your physical activity data including steps, calories, distance, and active minutes.

## Features

- OAuth 2.0 authentication with Google Fit API
- Retrieves activity data for the last 7 days
- Tracks:
  - Steps
  - Calories burned
  - Distance traveled
  - Active minutes
- Automatic token refresh
- Environment variable support for credentials

## Prerequisites

- Python 3.7+
- Google Cloud Platform account
- Google Fit API enabled

## Setup Instructions

### 1. Enable Google Fit API

Using Google Cloud Console:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Library**
4. Search for "Fitness API" and enable it

Using gcloud CLI:
```bash
# Enable the Fitness API
gcloud services enable fitness.googleapis.com

# Verify it's enabled
gcloud services list --enabled | grep fitness
```

### 2. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Desktop app** as application type
4. Configure the OAuth consent screen if prompted
5. Add the following to your OAuth client:
   - **Authorized JavaScript origins**: `http://localhost:8080`
   - **Authorized redirect URIs**: `http://localhost:8080/`
6. Download the credentials JSON file or note your:
   - Client ID
   - Client Secret

### 3. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv
```

### 4. Configure Environment Variables

Create a .env file in the same directory as the script:

```env
GOOGLE_FIT_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_FIT_CLIENT_SECRET=your-client-secret
```

Replace your-client-id and your-client-secret with your actual OAuth credentials.

## Usage

### First Run (Authentication)

The first time you run the script, it will open a browser window for OAuth authorization:

```bash
python3 google_fit_setup.py
```

1. A browser window will open
2. Sign in with your Google account
3. Grant the requested permissions
4. The script will save a token.json file for future use

### Subsequent Runs

After the initial authentication, the script will use the saved token:

```bash
python3 google_fit_setup.py
```

The token will be automatically refreshed when it expires.

## Output Example

```
==================================================
Google Fit API - Activity Data Retrieval
==================================================
Starting OAuth 2.0 authentication flow...
Authentication successful! Token saved to token.json

Connecting to Google Fit API...

Fetching data from 2026-07-31 to 2026-08-07
✓ Steps: 45230.00
✓ Calories: 12450.50 kcal
✓ Distance: 32500.00 meters
✓ Active Minutes: 420.00 min

==================================================
Summary (Last 7 days):
==================================================
Steps: 45230
Calories: 12450.50 kcal
Distance: 32500.00 meters
Active Minutes: 420 min
==================================================
```

## Files Generated

- credentials.json - Temporary file created from environment variables (auto-generated)
- token.json - OAuth token for authenticated sessions (saved after first run)

## Security Notes

- Never commit .env, credentials.json, or token.json to version control
- Add them to your .gitignore:
  ```
  .env
  credentials.json
  token.json
  ```
- Keep your Client ID and Client Secret secure
- The token has access to your fitness data

## Troubleshooting

### "Missing GOOGLE_FIT_CLIENT_ID or GOOGLE_FIT_CLIENT_SECRET"
- Ensure your .env file exists and contains both variables
- Check that the .env file is in the same directory as the script

### "Access blocked: This app's request is invalid"
- Verify your redirect URIs in Google Cloud Console match http://localhost:8080/
- Ensure the Fitness API is enabled for your project

### "Token has been expired or revoked"
- Delete token.json and run the script again to re-authenticate

### Port 8080 already in use
- Modify the port=8080 parameter in the script to use a different port
- Update the redirect URI in Google Cloud Console to match

## API Scopes

The script requests the following scopes:
- fitness.activity.read - Read activity data
- fitness.location.read - Read location data
- fitness.body.read - Read body measurements

## License

MIT License - Feel free to use and modify as needed.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

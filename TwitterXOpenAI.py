import hashlib
import base64
import os
import requests
from urllib.parse import urlencode, urlparse, parse_qs
import webbrowser
import openai

# Configuration for OAuth 2.0
client_id = 'T093NXZzcnAwVjJKbFRtWkhOdWs6MTpjaQ'
client_secret = 'UWIbzDqksLVSelpQj66UKPTVE4ftj_uMXJ5BVl0MZ6DCGrYytN'  # Add your client secret here if it's required for your app
redirect_uri = 'http://127.0.0.1/'
scope = 'tweet.read tweet.write users.read offline.access'
code_challenge_method = 'S256'

# Generate a code verifier and challenge
code_verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b'=').decode('utf-8')
code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).rstrip(b'=').decode('utf-8')

# Construct the authorization URL
auth_params = {
    'response_type': 'code',
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'scope': scope,
    'state': 'state',
    'code_challenge': code_challenge,
    'code_challenge_method': code_challenge_method,
}

authorization_url = f"https://twitter.com/i/oauth2/authorize?{urlencode(auth_params)}"

# Step 1: Direct the user to the authorization URL
print(f"Go to the following URL to authorize:\n{authorization_url}")
webbrowser.open(authorization_url)

# Step 2: User authorizes the app and is redirected back with the authorization code
print("After authorizing, you will be redirected to a URL that starts with your redirect URI.")
print("Please paste the full URL (including the code parameter) here:")
redirected_url = input("Paste the full URL here: ")

# Extract the authorization code from the redirected URL
parsed_url = urlparse(redirected_url)
authorization_code = parse_qs(parsed_url.query).get('code', [None])[0]

if not authorization_code:
    print("Error: No authorization code found in the URL. Please ensure you pasted the correct URL.")
    exit()

# Step 3: Exchange the authorization code for an access token
token_url = 'https://api.twitter.com/2/oauth2/token'
token_data = {
    'grant_type': 'authorization_code',
    'client_id': client_id,
    'client_secret': client_secret,  # If your app requires a client secret
    'redirect_uri': redirect_uri,
    'code_verifier': code_verifier,
    'code': authorization_code,
}
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': f'Basic {base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()}'
}

response = requests.post(token_url, data=token_data, headers=headers)
token_response_data = response.json()

# Extract the access token
access_token = token_response_data.get('access_token')
refresh_token = token_response_data.get('refresh_token')

if access_token is None:
    print("Error: Failed to retrieve access token. Response data:")
    print(token_response_data)
    exit()

print(f"Access Token: {access_token}")
print(f"Refresh Token: {refresh_token}")

# Step 4: Generate content using OpenAI
openai_api_key = "sk-jlfEUEj_tr1lpYN3W5ZJcV4Ei1kLy8o4SGQo1HBZuAT3BlbkFJexbZEnhwyFFroFZmVAzM0SeGLWNx5xTXo35SySZSwA"

# Initialize the OpenAI client with the correct API key
client = openai.OpenAI(api_key=openai_api_key)

prompt = """
Generate a social media post for Twitter (X) that engages the audience in a discussion about the future of AI in everyday life. 
The tone should be friendly, encouraging interaction, and invite followers to share their thoughts and experiences.
"""

# Generate the content using OpenAI
response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": prompt}
    ],
    model="gpt-4",
)

# Access the generated post content
post_content = response.choices[0].message.content.strip()

# Step 5: Post the content to Twitter using the access token
tweet_url = "https://api.twitter.com/2/tweets"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
payload = {
    "text": post_content
}

response = requests.post(tweet_url, json=payload, headers=headers)

if response.status_code == 201:
    print("Successfully posted to Twitter")
else:
    print(f"Failed to post to Twitter: {response.status_code}")
    print(response.json())

#!/usr/bin/env python3
from dotenv import dotenv_values
import requests
import json

class SpotifyClient:
    def __init__(self, client_id, secret):
        self.client_id = client_id
        self.secret = secret

    def get_access_token(self):
        r = requests.post('https://accounts.spotify.com/api/token', {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.secret
        })
        response = json.loads(r.text)
        return response['access_token']

    def api_req(self, uri):
        url = 'https://api.spotify.com/v1' + uri
        r = requests.get(url, headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {token}'.format(token=self.get_access_token())
            })
        return json.loads(r.text)

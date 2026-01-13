"""InvertirOnline API client for fetching cauciones prices."""

import requests
from typing import Optional


class IOLClient:
    """Client for interacting with InvertirOnline API."""

    BASE_URL = "https://api.invertironline.com"
    TOKEN_URL = f"{BASE_URL}/token"

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def authenticate(self) -> bool:
        """Authenticate with IOL API and obtain access token."""
        payload = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password"
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(self.TOKEN_URL, data=payload, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print("Authentication successful")
                return True

            print(f"Authentication failed: {response.status_code} - {response.text}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Authentication error: {e}")
            return False

    def _get_headers(self) -> dict:
        """Get headers with authorization token."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_cauciones(self) -> list:
        """Fetch all cauciones prices from IOL API."""
        if not self.access_token:
            if not self.authenticate():
                return []

        # Try the correct endpoint for cauciones
        # The API uses: /api/v2/{mercado}/Titulos/{instrumento}
        url = f"{self.BASE_URL}/api/v2/bCBA/Titulos/cauciones"
        
        try:
            print(f"Fetching cauciones from: {url}")
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 401:
                print("Token expired, re-authenticating...")
                if self.authenticate():
                    response = requests.get(url, headers=self._get_headers(), timeout=30)
                else:
                    return []

            if response.status_code == 200:
                data = response.json()
                print(f"Received {len(data.get('titulos', data)) if isinstance(data, dict) else len(data)} cauciones")
                # The response might be nested under 'titulos'
                if isinstance(data, dict) and 'titulos' in data:
                    return data['titulos']
                return data if isinstance(data, list) else []

            print(f"Failed to fetch cauciones: {response.status_code}")
            print(f"Response: {response.text[:500] if response.text else 'Empty'}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []

    def get_caucion_by_days(self, days: int) -> Optional[dict]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()

        for caucion in cauciones:
            plazo = caucion.get("plazo") or caucion.get("diasVencimiento")
            if plazo == days:
                return caucion

        return None

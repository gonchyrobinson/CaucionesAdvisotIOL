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

        response = requests.post(self.TOKEN_URL, data=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.refresh_token = data.get("refresh_token")
            return True

        print(f"Authentication failed: {response.status_code} - {response.text}")
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

        url = f"{self.BASE_URL}/api/v2/Cotizaciones/Cauciones/argentina"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code == 401:
            # Token expired, try to re-authenticate
            if self.authenticate():
                response = requests.get(url, headers=self._get_headers())
            else:
                return []

        if response.status_code == 200:
            return response.json()

        print(f"Failed to fetch cauciones: {response.status_code} - {response.text}")
        return []

    def get_caucion_by_days(self, days: int) -> Optional[dict]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()

        for caucion in cauciones:
            if caucion.get("plazo") == days:
                return caucion

        return None

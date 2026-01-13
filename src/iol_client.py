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

        # Try multiple possible endpoints for cauciones
        endpoints_to_try = [
            "/api/v2/Cotizaciones/Cauciones",
            "/api/v2/argentina/Titulos/Cauciones", 
            "/api/v2/bCBA/Titulos/Cauciones",
            "/api/v2/Cotizaciones/Instrumentos/Cauciones",
            "/api/v2/Titulos/Cauciones/bCBA",
        ]
        
        for endpoint in endpoints_to_try:
            url = f"{self.BASE_URL}{endpoint}"
            try:
                print(f"Trying endpoint: {url}")
                response = requests.get(url, headers=self._get_headers(), timeout=30)

                if response.status_code == 401:
                    print("Token expired, re-authenticating...")
                    if self.authenticate():
                        response = requests.get(url, headers=self._get_headers(), timeout=30)
                    else:
                        continue

                if response.status_code == 200:
                    data = response.json()
                    print(f"SUCCESS with endpoint: {endpoint}")
                    print(f"Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Keys: {data.keys()}")
                        if 'titulos' in data:
                            return data['titulos']
                        return [data] if data else []
                    return data if isinstance(data, list) else []

                print(f"  -> {response.status_code}: {response.text[:200] if response.text else 'Empty'}")
                
            except requests.exceptions.RequestException as e:
                print(f"  -> Request error: {e}")
                continue
        
        print("All endpoints failed")
        return []

    def get_caucion_by_days(self, days: int) -> Optional[dict]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()

        for caucion in cauciones:
            plazo = caucion.get("plazo") or caucion.get("diasVencimiento")
            if plazo == days:
                return caucion

        return None

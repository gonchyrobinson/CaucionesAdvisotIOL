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
        """Fetch cauciones prices from IOL API by querying individual symbols."""
        if not self.access_token:
            if not self.authenticate():
                return []

        # Cauciones have symbols like CAUC1D, CAUC7D, CAUC14D, etc. (1 day, 7 days, 14 days)
        # The format is: /api/v2/{mercado}/Titulos/{simbolo}/Cotizacion
        caucion_symbols = [
            ("CAUC1D", 1),   # 1 day
            ("CAUC7D", 7),   # 7 days
            ("CAUC14D", 14), # 14 days
            ("CAUC30D", 30), # 30 days
        ]
        
        mercados = ["bCBA", "BCBA", "argentina"]
        cauciones = []
        
        # First, try to get the panel of cauciones
        panel_endpoints = [
            "/api/v2/Cotizaciones/Panel/Cauciones/argentina",
            "/api/v2/bCBA/Titulos/Cauciones/Cotizacion",
        ]
        
        for endpoint in panel_endpoints:
            url = f"{self.BASE_URL}{endpoint}"
            try:
                print(f"Trying panel: {url}")
                response = requests.get(url, headers=self._get_headers(), timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    print(f"SUCCESS with panel: {endpoint}")
                    print(f"Data: {data}")
                    if isinstance(data, dict) and 'titulos' in data:
                        return data['titulos']
                    if isinstance(data, list):
                        return data
                print(f"  -> {response.status_code}")
            except Exception as e:
                print(f"  -> Error: {e}")
        
        # If panels fail, try individual symbols
        for mercado in mercados:
            print(f"Trying mercado: {mercado}")
            for symbol, days in caucion_symbols:
                url = f"{self.BASE_URL}/api/v2/{mercado}/Titulos/{symbol}/Cotizacion"
                try:
                    response = requests.get(url, headers=self._get_headers(), timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        data['plazo'] = days
                        data['symbol'] = symbol
                        cauciones.append(data)
                        print(f"  Got {symbol}: {data.get('ultimoPrecio', 'N/A')}")
                except Exception as e:
                    continue
            
            if cauciones:
                print(f"Found {len(cauciones)} cauciones in {mercado}")
                return cauciones
        
        # Try alternative approach - get all instruments and filter
        print("Trying to get all instruments...")
        try:
            url = f"{self.BASE_URL}/api/v2/Operaciones"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"Operaciones response keys: {data.keys() if isinstance(data, dict) else type(data)}")
        except Exception as e:
            print(f"Operaciones error: {e}")
        
        print("Could not fetch cauciones data")
        return cauciones

    def get_caucion_by_days(self, days: int) -> Optional[dict]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()

        for caucion in cauciones:
            plazo = caucion.get("plazo") or caucion.get("diasVencimiento")
            if plazo == days:
                return caucion

        return None

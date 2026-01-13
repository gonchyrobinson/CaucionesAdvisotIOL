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
        """Fetch cauciones prices from IOL API."""
        if not self.access_token:
            if not self.authenticate():
                return []

        cauciones = []
        
        # Based on API docs: /api/v2/{mercado}/Titulos/{simbolo}/Cotizacion
        # tipo includes: cAUCIONESPESOS, cAUCIONESDOLARES
        # Common caucion symbols in Argentina: PESOS (1 day), 7DIAS, 14DIAS, etc.
        
        # Possible caucion symbols - try various formats
        caucion_symbols = [
            # Pesos cauciones by days
            ("PESOS", 1), ("1", 1), ("CI1", 1),
            ("7DIAS", 7), ("7", 7), ("CI7", 7),
            ("14DIAS", 14), ("14", 14), ("CI14", 14),
            ("30DIAS", 30), ("30", 30), ("CI30", 30),
            # Alternative formats
            ("CAUC.1", 1), ("CAUC.7", 7), ("CAUC.14", 14), ("CAUC.30", 30),
            ("CAUCPESOS1", 1), ("CAUCPESOS7", 7),
        ]
        
        mercado = "bCBA"  # Main Argentine market
        
        # First try to get title info to discover the format
        print(f"Testing API with known stock symbol (GGAL)...")
        test_url = f"{self.BASE_URL}/api/v2/{mercado}/Titulos/GGAL/Cotizacion"
        try:
            response = requests.get(test_url, headers=self._get_headers(), timeout=30)
            print(f"GGAL test: {response.status_code}")
            if response.status_code == 200:
                print(f"API is working. Response sample: {str(response.json())[:200]}")
        except Exception as e:
            print(f"GGAL test error: {e}")
        
        # Try each caucion symbol
        print(f"\nTrying caucion symbols in mercado {mercado}...")
        for symbol, days in caucion_symbols:
            url = f"{self.BASE_URL}/api/v2/{mercado}/Titulos/{symbol}/Cotizacion"
            try:
                response = requests.get(url, headers=self._get_headers(), timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    data['plazo'] = days
                    data['symbol'] = symbol
                    cauciones.append(data)
                    print(f"  SUCCESS {symbol}: precio={data.get('ultimoPrecio', 'N/A')}")
                elif response.status_code != 404:
                    print(f"  {symbol}: {response.status_code}")
            except Exception as e:
                continue
        
        if cauciones:
            print(f"\nFound {len(cauciones)} cauciones")
            return cauciones
        
        # If no cauciones found, try to list all available instruments
        print("\nNo cauciones found with known symbols.")
        print("You may need to check InvertirOnline's platform for exact caucion symbols.")
        print("Or contact IOL support to get the list of caucion symbols available via API.")
        
        return cauciones

    def get_caucion_by_days(self, days: int) -> Optional[dict]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()

        for caucion in cauciones:
            plazo = caucion.get("plazo") or caucion.get("diasVencimiento")
            if plazo == days:
                return caucion

        return None

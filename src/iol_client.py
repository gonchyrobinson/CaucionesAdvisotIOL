"""InvertirOnline API client for fetching market data."""

import requests
from typing import Optional, List, Dict, Any


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

    def get_cotizacion(self, symbol: str, mercado: str = "bCBA") -> Optional[Dict[str, Any]]:
        """Get cotizacion for a specific symbol."""
        if not self.access_token:
            if not self.authenticate():
                return None

        url = f"{self.BASE_URL}/api/v2/{mercado}/Titulos/{symbol}/Cotizacion"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None

    def get_cauciones(self) -> List[Dict[str, Any]]:
        """
        Fetch cauciones data from IOL API.
        
        Note: Cauciones in IOL are not accessed via traditional symbols.
        They are selected by currency (ARS/USD) + days in the web interface.
        The API might not expose caucion rates directly.
        """
        if not self.access_token:
            if not self.authenticate():
                return []

        # Test API connectivity
        print("Testing API with GGAL...")
        ggal = self.get_cotizacion("GGAL", "bCBA")
        if ggal:
            print(f"API working. GGAL: ${ggal.get('ultimoPrecio', 'N/A')}")
        else:
            print("Warning: Could not fetch GGAL")

        # Try to find caucion endpoints
        # Based on API docs, tipo includes: cAUCIONESPESOS, cAUCIONESDOLARES
        endpoints = [
            "/api/v2/Cotizaciones/Cauciones",
            "/api/v2/Cauciones",
            "/api/v2/Operaciones",
        ]

        print("\nSearching for caucion data...")
        for endpoint in endpoints:
            url = f"{self.BASE_URL}{endpoint}"
            try:
                response = requests.get(url, headers=self._get_headers(), timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    print(f"Found data at {endpoint}: {type(data).__name__}")
                    
                    if isinstance(data, list):
                        print(f"  Items count: {len(data)}")
                        # Print first few items to understand structure
                        for i, item in enumerate(data[:5]):
                            print(f"  [{i}]: {item}")
                        
                        # Look for caucion-related items
                        caucion_items = [
                            item for item in data 
                            if isinstance(item, dict) and 
                            ('caucion' in str(item).lower() or 'cauc' in str(item).lower())
                        ]
                        if caucion_items:
                            print(f"\n  Found {len(caucion_items)} caucion-related items:")
                            for item in caucion_items[:3]:
                                print(f"    {item}")
                            return caucion_items
                    
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                        print(f"  Sample: {str(data)[:500]}")
            except Exception as e:
                print(f"  Error: {e}")
                continue

        print("\n" + "="*60)
        print("CAUCIONES NOT AVAILABLE VIA API")
        print("="*60)
        print("The IOL API does not appear to expose caucion rates.")
        print("Cauciones are selected by currency + days in the web UI,")
        print("not by traditional stock symbols.")
        print("")
        print("Options:")
        print("1. Contact IOL support to ask about caucion API access")
        print("2. Use web scraping (requires different approach)")
        print("3. Monitor stocks instead of cauciones")
        print("="*60)
        
        return []

    def get_caucion_by_days(self, days: int) -> Optional[Dict[str, Any]]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()
        for caucion in cauciones:
            if caucion.get("plazo") == days:
                return caucion
        return None

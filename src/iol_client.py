"""InvertirOnline API client using iol-api library."""

import asyncio
from typing import Optional, List, Dict, Any

from iol_api import IOLClient
from iol_api.constants import Mercado


class IOLClientWrapper:
    """Wrapper around iol-api library for fetching cauciones data."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self._client: Optional[IOLClient] = None

    def _get_client(self) -> IOLClient:
        """Get or create IOL client instance."""
        if self._client is None:
            self._client = IOLClient(self.username, self.password)
        return self._client

    async def _get_titulo_async(self, symbol: str, mercado: Mercado = Mercado.BCBA) -> Optional[Dict[str, Any]]:
        """Get titulo data asynchronously."""
        try:
            client = self._get_client()
            data = await client.get_titulo(symbol, mercado)
            return data
        except Exception as e:
            print(f"Error getting {symbol}: {e}")
            return None

    async def _get_cotizacion_async(self, symbol: str, mercado: Mercado = Mercado.BCBA) -> Optional[Dict[str, Any]]:
        """Get cotizacion data asynchronously."""
        try:
            client = self._get_client()
            data = await client.get_cotizacion(symbol, mercado)
            return data
        except Exception as e:
            print(f"Error getting cotizacion for {symbol}: {e}")
            return None

    async def _get_cauciones_async(self) -> List[Dict[str, Any]]:
        """Fetch cauciones data asynchronously."""
        cauciones = []
        
        # Test API connectivity first
        print("Testing API connectivity with GGAL...")
        test_data = await self._get_cotizacion_async("GGAL", Mercado.BCBA)
        if test_data:
            print(f"API working. GGAL price: {test_data.get('ultimoPrecio', 'N/A')}")
        else:
            print("Warning: Could not fetch GGAL data")
        
        # Try to get cauciones - possible symbol formats
        # In IOL, cauciones might use symbols like: PESOS1D, PESOS7D, etc.
        caucion_symbols = [
            ("PESOS1D", 1), ("PESOS7D", 7), ("PESOS14D", 14), ("PESOS30D", 30),
            ("1D", 1), ("7D", 7), ("14D", 14), ("30D", 30),
            ("CAUC1", 1), ("CAUC7", 7), ("CAUC14", 14), ("CAUC30", 30),
        ]
        
        print("\nTrying caucion symbols...")
        for symbol, days in caucion_symbols:
            data = await self._get_cotizacion_async(symbol, Mercado.BCBA)
            if data and data.get('ultimoPrecio'):
                data['plazo'] = days
                data['symbol'] = symbol
                cauciones.append(data)
                print(f"  Found {symbol}: {data.get('ultimoPrecio')}")
        
        if not cauciones:
            print("\nNo cauciones found with standard symbols.")
            print("The iol-api library might not support cauciones directly.")
            print("Cauciones in IOL are selected by currency + days, not by symbol.")
        
        return cauciones

    def get_cauciones(self) -> List[Dict[str, Any]]:
        """Fetch cauciones data (sync wrapper)."""
        return asyncio.run(self._get_cauciones_async())

    def get_caucion_by_days(self, days: int) -> Optional[Dict[str, Any]]:
        """Get caucion data for a specific number of days."""
        cauciones = self.get_cauciones()
        
        for caucion in cauciones:
            if caucion.get("plazo") == days:
                return caucion
        
        return None


# Alias for backwards compatibility
IOLClient = IOLClientWrapper

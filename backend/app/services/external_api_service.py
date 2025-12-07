import httpx
from typing import List, Dict, Any

from ..config import settings


class ExternalApiService:
    """Service for fetching data from external APIs"""
    
    def __init__(self):
        self.base_url = settings.dummyjson_base_url
    
    async def fetch_products(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Fetch products from dummyjson API"""
        url = f"{self.base_url}/products"
        params = {"limit": limit}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("products", [])
    
    async def fetch_carts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch carts from dummyjson API"""
        url = f"{self.base_url}/carts"
        params = {"limit": limit}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("carts", [])

import aiohttp
import asyncio
from utils.logger import setup_logger

class DexScreener:
    def __init__(self):
        self.logger = setup_logger("dexscreener")
        self.session = None
        
    async def initialize(self):
        """Initialize DexScreener connection"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            
    async def test_connection(self):
        """Test connection to DexScreener API"""
        try:
            if not self.session:
                await self.initialize()
                
            url = "https://api.dexscreener.com/latest/dex/search?q=SOL/USDC"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return 'pairs' in data
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {str(e)}")
            return False
        
    async def close(self):
        """Close the API session"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def _make_request(self, endpoint):
        """Make API request with rate limiting and retries"""
        if not self.session:
            await self.initialize()
            
        async with self.request_semaphore:  # Rate limit requests
            for attempt in range(3):  # 3 retries
                try:
                    url = f"{self.base_url}/{endpoint}"
                    self.logger.info(f"Making request to: {url}")
                    
                    async with self.session.get(url, timeout=30) as response:
                        self.logger.info(f"Response status: {response.status}")
                        
                        if response.status == 200:
                            data = await response.json()
                            # Debug log the response
                            self.logger.info(f"Response data: {data}")
                            
                            # Ensure we have a valid response
                            if isinstance(data, dict):
                                if 'pairs' in data:
                                    return data
                                else:
                                    self.logger.error("Response missing 'pairs' key")
                            else:
                                self.logger.error(f"Unexpected response format: {type(data)}")
                            
                        elif response.status == 429:  # Rate limit
                            wait_time = int(response.headers.get('Retry-After', 60))
                            self.logger.warning(f"Rate limit hit, waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                            
                        else:
                            response_text = await response.text()
                            self.logger.error(
                                f"API error: {response.status}\n"
                                f"URL: {url}\n"
                                f"Response: {response_text}"
                            )
                            
                except asyncio.TimeoutError:
                    self.logger.error(f"Request timeout on attempt {attempt + 1}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        
                except Exception as e:
                    self.logger.error(f"Request error on attempt {attempt + 1}: {str(e)}")
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        
            self.logger.error("All retry attempts failed")
            return {'pairs': []}  # Return empty pairs list instead of None
            
    async def get_solana_pairs(self):
        """Get all Solana pairs"""
        try:
            result = await self._make_request("dex/pairs/solana")
            if not result or 'pairs' not in result:
                self.logger.error("Invalid response format for Solana pairs")
                return {'pairs': []}
            return result
        except Exception as e:
            self.logger.error(f"Error getting Solana pairs: {str(e)}")
            return {'pairs': []}
        
    async def get_token_pairs(self, token_address):
        """Get pairs for specific token"""
        return await self._make_request(f"dex/tokens/{token_address}")
        
    async def search_pairs(self, query):
        """Search for pairs"""
        return await self._make_request(f"dex/search?q={query}") 
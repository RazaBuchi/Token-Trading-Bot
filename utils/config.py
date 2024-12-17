from pathlib import Path
import yaml
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')
        if not self.WALLET_PRIVATE_KEY:
            raise ValueError("WALLET_PRIVATE_KEY not found in environment variables")
        self._load_config()

    def _load_config(self):
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            # Network settings
            self.RPC_ENDPOINT = config['network']['rpc_endpoints'][0]
            self.MAX_RETRIES = config['network']['max_retries']
            self.TIMEOUT = config['network']['timeout']
            
            # Trading settings
            trading = config['trading']
            self.POSITION_SIZE_SOL = trading['position_size_sol']
            self.MAX_HOLDINGS = trading['max_holdings']
            
            # Slippage settings
            self.BUY_SLIPPAGE = trading['slippage']['buy']
            self.SELL_SLIPPAGE = trading['slippage']['sell']
            
            # Other trading parameters
            self.MIN_LIQUIDITY = trading['min_liquidity']
            self.MIN_VOLUME = trading['min_volume']
            self.TAKE_PROFIT = trading['take_profit']
            self.STOP_LOSS = trading['stop_loss']
            self.DEX_SOURCES = trading['dex_sources']
            
            # Monitor settings
            self.CHECK_INTERVAL = trading['monitor_settings']['check_interval']
            self.PRICE_UPDATE = trading['monitor_settings']['price_update']
            self.MAX_AGE = trading['monitor_settings']['max_age']
            
            # Performance settings
            self.MEMORY_LIMIT_MB = config['performance']['memory_limit_mb']
            self.MAX_LATENCY_MS = config['performance']['max_latency_ms']
            self.MIN_EXECUTION_SPEED_MS = config['performance']['min_execution_speed_ms']
            
            # Wallet settings
            if 'wallet' in config:
                self.WALLET = {
                    'address': config['wallet']['address'],
                    'type': config['wallet'].get('type', 'phantom'),
                    'mode': config['wallet'].get('mode', 'active')
                }
            else:
                # Fallback to old config format
                self.WALLET = {
                    'address': 'your_phantom_wallet_address_here'
                }

        except Exception as e:
            print(f"Error loading config: {str(e)}")
            raise

# API Configuration
RAYDIUM_API_URL = "https://api.raydium.io/v2"
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest"

# Trading Parameters
POSITION_SIZE_SOL = 0.1  # Amount of SOL per trade
BUY_SLIPPAGE = 0.01  # 1% default slippage
SELL_SLIPPAGE = 0.01  # 1% default slippage

# Wallet Configuration
WALLET_PRIVATE_KEY = os.getenv('WALLET_PRIVATE_KEY')
RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"  # or your preferred RPC

config = Config()

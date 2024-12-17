import asyncio
import webbrowser
import json
import yaml
from solders.pubkey import Pubkey
from utils.logger import setup_logger
from utils.exceptions import WalletError

class PhantomConnector:
    def __init__(self):
        self.logger = setup_logger("phantom_connector")
        self.connection_url = "https://phantom.app/ul/connect"
        self.public_key = None
        
    async def connect(self):
        """Connect to Phantom Wallet"""
        try:
            self.logger.info("\n=== Connecting to Phantom Wallet ===")
            
            # 1. Open Phantom connection URL
            self.logger.info("Opening Phantom wallet...")
            webbrowser.open(self.connection_url)
            
            # 2. Wait for user to connect
            self.logger.info(
                "\nPlease follow these steps:"
                "\n1. Click 'Connect' in the Phantom popup"
                "\n2. Select your wallet"
                "\n3. Approve the connection"
            )
            
            # 3. Get wallet address from user
            wallet_address = input("\nEnter your Phantom wallet address: ").strip()
            
            # 4. Validate address format
            try:
                self.public_key = Pubkey.from_string(wallet_address)
                self.logger.info(f"✅ Wallet address validated: {self.public_key}")
            except ValueError:
                raise WalletError("Invalid wallet address format")
                
            # 5. Save wallet config
            self._save_wallet_config(wallet_address)
            
            self.logger.info("✅ Wallet connected successfully!")
            return wallet_address
            
        except Exception as e:
            self.logger.error(f"❌ Wallet connection failed: {str(e)}")
            raise
            
    def _save_wallet_config(self, wallet_address):
        """Save wallet configuration"""
        try:
            # First try to load existing config
            try:
                with open('config.yaml', 'r') as f:
                    config = yaml.safe_load(f) or {}
            except FileNotFoundError:
                config = {}
            
            # Update wallet config
            if 'phantom' not in config:
                config['phantom'] = {}
            config['phantom']['public_key'] = wallet_address
            
            # Save updated config
            with open('config.yaml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
                
            self.logger.info("✅ Wallet configuration saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save wallet config: {str(e)}")
            raise
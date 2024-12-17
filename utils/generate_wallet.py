from solders.keypair import Keypair
import base58
import os

def generate_new_wallet():
    try:
        # Generate new keypair
        keypair = Keypair()
        
        # Get private key as bytes (all 64 bytes)
        secret_key_bytes = bytes(keypair.secret())
        # Convert to base58
        private_key = base58.b58encode(secret_key_bytes).decode('ascii')
        # Get public key
        wallet_address = str(keypair.pubkey())
        
        print(f"\nNew Wallet Generated:")
        print(f"Wallet Address (Public Key): {wallet_address}")
        print(f"Private Key (base58): {private_key}")
        
        return wallet_address, private_key
    except Exception as e:
        print(f"Error generating wallet: {str(e)}")
        return None, None

if __name__ == "__main__":
    wallet_address, private_key = generate_new_wallet()
    if wallet_address and private_key:
        # Save to .env file
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
        with open(env_path, 'w') as f:
            f.write(f"PHANTOM_WALLET_ADDRESS={wallet_address}\n")
            f.write(f"WALLET_PRIVATE_KEY={private_key}\n")
        print("\nWallet details saved to .env file") 
import asyncio
from wallet_manager import WalletManager
from logger import setup_logger

async def check_wallet_balance():
    logger = setup_logger("balance_checker")
    wallet = WalletManager()
    
    try:
        await wallet.initialize()
        balance = await wallet.check_balance()
        
        if balance == 0:
            logger.info(
                "\nTo fund your wallet:"
                "\n1. Open Phantom wallet"
                "\n2. Click 'Deposit'"
                "\n3. Select 'SOL'"
                "\n4. Transfer SOL to your wallet"
                "\n5. Wait for confirmation"
                "\n\nRecommended minimum: 0.5 SOL"
            )
        else:
            logger.info(f"\nWallet balance: {balance:.4f} SOL")
            
    except Exception as e:
        logger.error(f"Error checking balance: {str(e)}")
    finally:
        await wallet.cleanup()

if __name__ == "__main__":
    asyncio.run(check_wallet_balance()) 
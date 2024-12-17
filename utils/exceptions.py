class TradingBotError(Exception):
    """Base exception class for trading bot errors"""
    pass

class InsufficientBalanceError(TradingBotError):
    """Raised when wallet balance is insufficient for trade"""
    pass

class InvalidTokenError(TradingBotError):
    """Raised when token validation fails"""
    pass

class WalletError(TradingBotError):
    """Raised when there are wallet-related issues"""
    pass

class NetworkError(TradingBotError):
    """Raised when there are network-related issues"""
    pass

class ConfigError(TradingBotError):
    """Raised when there are configuration-related issues"""
    pass

class MarketCapError(TradingBotError):
    """Raised when market cap validation fails"""
    pass

class PoolError(TradingBotError):
    """Raised when there are liquidity pool-related issues"""
    pass

class TransactionError(TradingBotError):
    """Raised when transaction execution fails"""
    pass

class TokenAccountError(TradingBotError):
    """Raised when there are token account-related issues"""
    pass 
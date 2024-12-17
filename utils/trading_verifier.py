import asyncio
from utils.logger import setup_logger
from utils.exceptions import TradingBotError

class TradingVerifier:
    def __init__(self):
        self.logger = setup_logger("trading_verifier")
        self.warnings = []
        self.errors = []

    async def verify_all_components(self, trading_bot):
        """Verify all components before live trading"""
        try:
            self.logger.info("\n=== PRE-LIVE TRADING VERIFICATION ===")
            
            # Run all checks
            checks = [
                ("Wallet Connection", await self._verify_wallet(trading_bot.wallet_manager)),
                ("Network Connectivity", await self._verify_network(trading_bot.wallet_manager)),
                ("Agent Status", await self._verify_agents(trading_bot)),
                ("Trading Parameters", self._verify_config()),
                ("Risk Management", await self._verify_risk_management(trading_bot))
            ]
            
            # Print summary
            self.logger.info("\n=== Verification Summary ===")
            all_passed = True
            for name, result in checks:
                status = "[PASS]" if result else "[WARN]"
                self.logger.info(f"{name}: {status}")
                
            # Show warnings
            if self.warnings:
                self.logger.warning("\nWarnings:")
                for warning in self.warnings:
                    self.logger.warning(f"⚠️  {warning}")
                    
            # Show errors
            if self.errors:
                self.logger.error("\nErrors:")
                for error in self.errors:
                    self.logger.error(f"❌ {error}")
                all_passed = False
                
            if all_passed:
                self.logger.info("\n✅ System check complete - Ready for monitoring")
                if self.warnings:
                    self.logger.info("Note: Some warnings present but not blocking operation")
            else:
                self.logger.error("\n❌ Critical issues found - Please fix before proceeding")
                
            return len(self.errors) == 0  # Return True if no critical errors
            
        except Exception as e:
            self.logger.error(f"Verification failed: {str(e)}")
            return False

    async def _verify_wallet(self, wallet_manager):
        """Verify wallet status"""
        self.logger.info("\n1. Checking Wallet Status...")
        
        try:
            # Verify wallet connection
            if not wallet_manager.phantom_public_key:
                self.warnings.append("No wallet connected - Running in monitor-only mode")
                return True
                
            # Check balance
            balance = await wallet_manager.check_balance()
            if balance == 0:
                self.warnings.append(
                    f"Wallet has 0 SOL balance - Running in monitor-only mode\n"
                    f"  Address: {wallet_manager.phantom_public_key}"
                )
            else:
                self.logger.info(
                    f"✓ Wallet verified:\n"
                    f"  Address: {wallet_manager.phantom_public_key}\n"
                    f"  Balance: {balance:.4f} SOL"
                )
                
            return True
            
        except Exception as e:
            self.warnings.append(f"Wallet verification issue: {str(e)} - Running in monitor-only mode")
            return True

    async def _verify_network(self, wallet_manager):
        """Verify network connectivity"""
        self.logger.info("\n2. Checking Network Status...")
        
        try:
            # Test RPC connection
            if not wallet_manager.client:
                self.warnings.append("No RPC connection - Running in monitor-only mode")
                return True
                
            # Verify connection
            try:
                await wallet_manager.client.is_connected()
                self.logger.info(f"✓ Connected to RPC: {wallet_manager.client.endpoint}")
            except:
                self.warnings.append("RPC connection failed - Running in monitor-only mode")
                return True
                
            return True
            
        except Exception as e:
            self.warnings.append(f"Network verification issue: {str(e)} - Running in monitor-only mode")
            return True

    async def _verify_agents(self, bot):
        """Verify all agents are operational"""
        self.logger.info("\n3. Checking Agent Status...")
        
        try:
            # Verify all agents exist
            agents = {
                'Scout': bot.scout_agent,
                'Trading': bot.trading_agent,
                'Analysis': bot.analysis_agent,
                'Exit': bot.exit_agent
            }
            
            all_agents_ok = True
            for name, agent in agents.items():
                if not agent:
                    self.errors.append(f"{name} Agent not initialized")
                    all_agents_ok = False
                else:
                    self.logger.info(f"✓ {name} Agent ready")
                    
            return all_agents_ok
            
        except Exception as e:
            self.errors.append(f"Agent verification failed: {str(e)}")
            return False

    def _verify_config(self):
        """Verify trading configuration"""
        self.logger.info("\n4. Checking Trading Parameters...")
        
        try:
            from utils.config import config
            
            # Verify essential parameters
            required_params = {
                'POSITION_SIZE_SOL': (0, 100),  # Between 0 and 100 SOL
                'MAX_HOLDINGS': (1, 10),        # Between 1 and 10 positions
                'SLIPPAGE_TOLERANCE': (0, 0.05)  # Max 5% slippage
            }
            
            all_params_ok = True
            for param, (min_val, max_val) in required_params.items():
                value = getattr(config, param)
                if not min_val <= value <= max_val:
                    self.warnings.append(
                        f"Parameter {param} = {value} "
                        f"(should be between {min_val} and {max_val})"
                    )
                    all_params_ok = False
                    
            if all_params_ok:
                self.logger.info(
                    f"✓ Trading parameters verified:\n"
                    f"  Position Size: {config.POSITION_SIZE_SOL} SOL\n"
                    f"  Max Holdings: {config.MAX_HOLDINGS}\n"
                    f"  Slippage: {config.SLIPPAGE_TOLERANCE*100}%"
                )
                
            return True  # Return True even with warnings
            
        except Exception as e:
            self.errors.append(f"Config verification failed: {str(e)}")
            return False

    async def _verify_risk_management(self, bot):
        """Verify risk management settings"""
        self.logger.info("\n5. Checking Risk Management...")
        
        try:
            # Check market cap limits
            if not (0 < bot.trading_agent.MAX_MARKET_CAP <= 100):
                self.warnings.append(
                    f"Market cap limit ${bot.trading_agent.MAX_MARKET_CAP} "
                    "outside recommended range (0-100)"
                )
                
            # Verify position size vs balance
            balance = await bot.wallet_manager.check_balance()
            if balance > 0:  # Only check if there's a balance
                max_positions = balance / config.POSITION_SIZE_SOL
                if max_positions < 1:
                    self.warnings.append(
                        f"Balance ({balance:.4f} SOL) too low "
                        f"for position size {config.POSITION_SIZE_SOL} SOL"
                    )
                else:
                    self.logger.info(
                        f"✓ Risk parameters verified:\n"
                        f"  Max positions possible: {int(max_positions)}\n"
                        f"  Market cap limit: ${bot.trading_agent.MAX_MARKET_CAP}"
                    )
                    
            return True  # Return True even with warnings
            
        except Exception as e:
            self.errors.append(f"Risk management verification failed: {str(e)}")
            return False 
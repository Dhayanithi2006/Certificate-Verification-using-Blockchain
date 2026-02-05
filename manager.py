# backend/app/blockchain/manager.py
"""
Blockchain Manager - Singleton for blockchain operations
"""

from datetime import datetime
from typing import Dict
from .core import Blockchain
from .smart_contract import CertificateSmartContract

class BlockchainManager:
    """Singleton manager for blockchain operations"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BlockchainManager, cls).__new__(cls)
            cls._instance.init_blockchain()
        return cls._instance
    
    def init_blockchain(self):
        """Initialize or load blockchain"""
        print("🔄 Initializing blockchain...")
        self.blockchain = Blockchain.load_from_file()
        if not self.blockchain:
            self.blockchain = Blockchain(difficulty=2)  # Lower difficulty for testing
            print("✅ New blockchain created")
        else:
            print(f"✅ Blockchain loaded with {len(self.blockchain.chain)} blocks")
        
        self.smart_contract = CertificateSmartContract()
        print(f"✅ Smart contract initialized")
    
    def register_certificate(self, certificate_data: Dict) -> Dict:
        """Register a certificate on blockchain"""
        print(f"🔄 Registering certificate {certificate_data.get('certificate_number')}...")
        
        # Validate with smart contract first
        validation_result = self.smart_contract.validate_certificate(certificate_data)
        
        if not validation_result["valid"]:
            print(f"❌ Certificate failed smart contract validation")
            return {
                "success": False,
                "error": "Certificate failed smart contract validation",
                "validation_result": validation_result
            }
        
        # Add to blockchain
        try:
            block_hash = self.blockchain.add_certificate_transaction(certificate_data)
            cert_hash = self.blockchain.calculate_certificate_hash(certificate_data)
            
            print(f"✅ Certificate registered on blockchain")
            print(f"   Block Hash: {block_hash[:16]}...")
            print(f"   Cert Hash: {cert_hash[:16]}...")
            
            return {
                "success": True,
                "block_hash": block_hash,
                "block_index": len(self.blockchain.chain) - 1,
                "certificate_hash": cert_hash,
                "validation_result": validation_result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"❌ Error registering certificate: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_certificate(self, certificate_hash: str) -> Dict:
        """Verify certificate on blockchain"""
        print(f"🔄 Verifying certificate hash: {certificate_hash[:16]}...")
        return self.blockchain.verify_certificate(certificate_hash)
    
    def get_certificate_history(self, certificate_id: str) -> Dict:
        """Get certificate history from blockchain"""
        history = self.blockchain.get_certificate_history(certificate_id)
        
        return {
            "certificate_id": certificate_id,
            "total_transactions": len(history),
            "history": history,
            "exists": len(history) > 0
        }
    
    def get_blockchain_info(self) -> Dict:
        """Get blockchain information"""
        stats = self.blockchain.get_chain_stats()
        
        return {
            "blockchain_info": {
                "total_blocks": stats["total_blocks"],
                "total_certificates": stats["total_certificates"],
                "verified_certificates": stats["verified_certificates"],
                "chain_valid": stats["chain_valid"],
                "difficulty": stats["difficulty"],
                "latest_block_hash": stats["latest_block_hash"],
                "latest_block_index": stats["latest_block_index"]
            },
            "genesis_block": self.blockchain.chain[0].to_dict() if self.blockchain.chain else None,
            "latest_block": self.blockchain.get_latest_block().to_dict() if self.blockchain.chain else None
        }
    
    def validate_chain(self) -> Dict:
        """Validate entire blockchain"""
        is_valid = self.blockchain.is_chain_valid()
        
        return {
            "chain_valid": is_valid,
            "total_blocks": len(self.blockchain.chain),
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def get_recent_transactions(self, limit: int = 10) -> list:
        """Get recent certificate transactions"""
        recent = []
        count = 0
        
        for block in reversed(self.blockchain.chain):
            if block.data.get("transaction_type") == "certificate_registration":
                recent.append({
                    "block_index": block.index,
                    "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
                    "certificate_number": block.data.get("transaction", {}).get("certificate_number", "Unknown"),
                    "type": block.data.get("transaction", {}).get("certificate_type", "Unknown"),
                    "status": block.data.get("transaction", {}).get("verification_status", "pending"),
                    "block_hash": block.hash[:16] + "..."
                })
                count += 1
                if count >= limit:
                    break
        
        return recent
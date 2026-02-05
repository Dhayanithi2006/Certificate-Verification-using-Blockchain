# backend/app/blockchain/core.py
"""
Blockchain Core Implementation
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import pickle
import os

class Block:
    """Single block in the blockchain"""
    def __init__(self, index: int, timestamp: float, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True, default=str)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int):
        """Mine the block with proof-of-work"""
        target = "0" * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        print(f"✅ Block {self.index} mined: {self.hash[:16]}...")
    
    def to_dict(self) -> Dict:
        """Convert block to dictionary"""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "human_time": datetime.fromtimestamp(self.timestamp).isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }
    
    def validate(self) -> bool:
        """Validate block integrity"""
        calculated_hash = self.calculate_hash()
        return calculated_hash == self.hash

class Blockchain:
    """Main blockchain class"""
    def __init__(self, difficulty: int = 2):  # Lower difficulty for testing
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions = []
        
        # Create genesis block
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data={
                "type": "genesis",
                "message": "Certificate Verification Blockchain",
                "creator": "System",
                "timestamp": datetime.now().isoformat()
            },
            previous_hash="0" * 64  # 64 zeros for genesis
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        print("✅ Genesis block created")
    
    def get_latest_block(self) -> Block:
        """Get the latest block in the chain"""
        return self.chain[-1]
    
    def add_block(self, data: Dict) -> Block:
        """Add a new block to the chain"""
        latest_block = self.get_latest_block()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=latest_block.hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        
        # Save to file after adding
        self.save_to_file()
        
        return new_block
    
    def add_certificate_transaction(self, certificate_data: Dict) -> str:
        """Add a certificate verification transaction to blockchain"""
        transaction = {
            "type": "certificate_verification",
            "certificate_id": certificate_data.get("certificate_id"),
            "certificate_number": certificate_data.get("certificate_number"),
            "certificate_type": certificate_data.get("certificate_type"),
            "owner_id": certificate_data.get("owner_id"),
            "owner_name": certificate_data.get("owner_name", "Unknown"),
            "verification_status": certificate_data.get("verification_status", "pending"),
            "verified_by": certificate_data.get("verified_by"),
            "verified_at": datetime.now().isoformat(),
            "hash": self.calculate_certificate_hash(certificate_data),
            "metadata": {
                "confidence_score": certificate_data.get("confidence_score", 0),
                "file_hash": certificate_data.get("file_hash", ""),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        block = self.add_block({
            "transaction_type": "certificate_registration",
            "transaction": transaction
        })
        
        return block.hash
    
    def calculate_certificate_hash(self, certificate_data: Dict) -> str:
        """Calculate unique hash for a certificate"""
        cert_string = json.dumps({
            "certificate_number": certificate_data.get("certificate_number"),
            "owner_id": certificate_data.get("owner_id"),
            "file_hash": certificate_data.get("file_hash", ""),
            "timestamp": datetime.now().isoformat()
        }, sort_keys=True)
        
        return hashlib.sha256(cert_string.encode()).hexdigest()
    
    def verify_certificate(self, certificate_hash: str) -> Dict:
        """Verify if a certificate exists in blockchain"""
        for block in self.chain:
            if (block.data.get("transaction_type") == "certificate_registration" and 
                "transaction" in block.data):
                transaction = block.data.get("transaction", {})
                if transaction.get("hash") == certificate_hash:
                    return {
                        "exists": True,
                        "verified": True,
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "timestamp": block.timestamp,
                        "human_time": datetime.fromtimestamp(block.timestamp).isoformat(),
                        "transaction": transaction,
                        "verification_status": "VALID"
                    }
        
        return {"exists": False, "verified": False, "verification_status": "NOT_FOUND"}
    
    def get_certificate_history(self, certificate_id: str) -> List[Dict]:
        """Get complete history of a certificate from blockchain"""
        history = []
        
        for block in self.chain:
            if (block.data.get("transaction_type") == "certificate_registration" and 
                "transaction" in block.data):
                transaction = block.data.get("transaction", {})
                if transaction.get("certificate_id") == certificate_id:
                    history.append({
                        "block_index": block.index,
                        "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
                        "transaction": transaction,
                        "block_hash": block.hash
                    })
        
        return history
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if current block hash is valid
            if not current_block.validate():
                print(f"❌ Invalid hash at block {i}")
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                print(f"❌ Invalid previous hash at block {i}")
                return False
        
        return True
    
    def get_chain_stats(self) -> Dict:
        """Get blockchain statistics"""
        total_certificates = 0
        verified_certificates = 0
        
        for block in self.chain:
            if block.data.get("transaction_type") == "certificate_registration":
                total_certificates += 1
                transaction = block.data.get("transaction", {})
                if transaction.get("verification_status") == "verified":
                    verified_certificates += 1
        
        return {
            "total_blocks": len(self.chain),
            "total_certificates": total_certificates,
            "verified_certificates": verified_certificates,
            "chain_valid": self.is_chain_valid(),
            "difficulty": self.difficulty,
            "latest_block_hash": self.get_latest_block().hash if self.chain else None,
            "latest_block_index": len(self.chain) - 1
        }
    
    def save_to_file(self, filename: str = "blockchain_data.pkl"):
        """Save blockchain to file"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self, f)
            print(f"✅ Blockchain saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving blockchain: {e}")
    
    @staticmethod
    def load_from_file(filename: str = "blockchain_data.pkl"):
        """Load blockchain from file"""
        if os.path.exists(filename):
            try:
                with open(filename, 'rb') as f:
                    blockchain = pickle.load(f)
                print(f"✅ Blockchain loaded from {filename}")
                return blockchain
            except Exception as e:
                print(f"❌ Error loading blockchain: {e}")
        return None
    
    def to_dict(self) -> Dict:
        """Convert entire blockchain to dictionary"""
        return {
            "chain": [block.to_dict() for block in self.chain],
            "difficulty": self.difficulty,
            "length": len(self.chain),
            "is_valid": self.is_chain_valid()
        }
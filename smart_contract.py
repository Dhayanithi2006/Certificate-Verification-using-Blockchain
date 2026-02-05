# backend/app/blockchain/smart_contract.py
"""
Smart Contract for Certificate Validation
"""

from datetime import datetime

class CertificateSmartContract:
    """Smart contract for certificate validation rules"""
    
    @staticmethod
    def validate_certificate(certificate_data: Dict) -> Dict:
        """Validate certificate against smart contract rules"""
        rules_passed = []
        rules_failed = []
        
        # Rule 1: Certificate number must be present
        if certificate_data.get("certificate_number"):
            rules_passed.append("certificate_number_present")
        else:
            rules_failed.append("certificate_number_missing")
        
        # Rule 2: Owner ID must be present
        if certificate_data.get("owner_id"):
            rules_passed.append("owner_id_present")
        else:
            rules_failed.append("owner_id_missing")
        
        # Rule 3: File hash must be present (for integrity)
        if certificate_data.get("file_hash"):
            rules_passed.append("file_hash_present")
        else:
            rules_failed.append("file_hash_missing")
        
        # Rule 4: Confidence score must be above threshold
        min_confidence = 60  # Lower threshold for demo
        confidence = certificate_data.get("confidence_score", 0)
        if confidence >= min_confidence:
            rules_passed.append(f"confidence_score_above_{min_confidence}")
        else:
            rules_failed.append(f"confidence_score_below_{min_confidence}")
        
        # Calculate validation score
        total_rules = len(rules_passed) + len(rules_failed)
        validation_score = (len(rules_passed) / total_rules * 100) if total_rules > 0 else 0
        
        return {
            "valid": len(rules_failed) == 0,
            "validation_score": round(validation_score, 2),
            "rules_passed": rules_passed,
            "rules_failed": rules_failed,
            "total_rules": total_rules,
            "timestamp": datetime.now().isoformat()
        }
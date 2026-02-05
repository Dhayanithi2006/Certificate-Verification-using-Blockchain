# backend/app/blockchain/__init__.py
"""
Certificate Verification Blockchain Module
"""

from .core import Block, Blockchain
from .smart_contract import CertificateSmartContract
from .manager import BlockchainManager

__all__ = ['Block', 'Blockchain', 'CertificateSmartContract', 'BlockchainManager']
__version__ = '1.0.0'
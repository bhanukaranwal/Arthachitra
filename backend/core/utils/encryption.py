import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Handles encryption and decryption of sensitive data like API keys."""
    
    def __init__(self, password: str = None):
        if password is None:
            password = os.getenv("ENCRYPTION_PASSWORD", "arthachitra-default-key")
        
        self.password = password.encode()
        self.salt = b'arthachitra_salt'  # In production, use a random salt per user
        
    def _get_key(self) -> bytes:
        """Generate encryption key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string."""
        try:
            key = self._get_key()
            f = Fernet(key)
            encrypted = f.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt a string."""
        try:
            key = self._get_key()
            f = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted = f.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise

# Global encryption manager instance
encryption_manager = EncryptionManager()

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage."""
    return encryption_manager.encrypt(api_key)

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key for use."""
    return encryption_manager.decrypt(encrypted_key)

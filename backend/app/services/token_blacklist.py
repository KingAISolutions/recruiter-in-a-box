"""
Token blacklist service for JWT revocation.
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import TokenBlacklist


class TokenBlacklistService:
    """Service for managing token blacklist."""
    
    def __init__(self):
        # In-memory set for development (without Redis)
        # In production, use Redis for distributed blacklist
        self._blacklist: Set[str] = set()
    
    async def blacklist_token(
        self, 
        jti: str, 
        exp: datetime,
        db: AsyncSession,
        user_id: str = None
    ) -> bool:
        """
        Add a token to the blacklist.
        
        Args:
            jti: JWT ID (unique token identifier)
            exp: Token expiration time
            db: Database session
            user_id: User ID for audit purposes
        
        Returns:
            True if successfully blacklisted
        """
        try:
            # Add to in-memory set
            self._blacklist.add(jti)
            
            # Store in database for persistence
            blacklist_entry = TokenBlacklist(
                jti=jti,
                expires_at=exp,
                blacklisted_at=datetime.utcnow(),
                user_id=user_id,
            )
            db.add(blacklist_entry)
            await db.commit()
            
            return True
        except Exception:
            return False
    
    async def is_blacklisted(self, jti: str, db: AsyncSession) -> bool:
        """
        Check if a token is blacklisted.
        
        Args:
            jti: JWT ID to check
            db: Database session
        
        Returns:
            True if token is blacklisted
        """
        # Check in-memory first (fast path)
        if jti in self._blacklist:
            return True
        
        # Check database
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        entry = result.scalar_one_or_none()
        
        if entry:
            # Add to in-memory for faster future checks
            self._blacklist.add(jti)
            return True
        
        return False
    
    async def cleanup_expired(self, db: AsyncSession) -> int:
        """
        Remove expired entries from the blacklist.
        
        Returns:
            Number of entries removed
        """
        now = datetime.utcnow()
        
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.expires_at < now)
        )
        expired_entries = result.scalars().all()
        
        count = 0
        for entry in expired_entries:
            await db.delete(entry)
            self._blacklist.discard(entry.jti)
            count += 1
        
        await db.commit()
        
        # Also cleanup in-memory set
        expired_in_memory = {jti for jti in self._blacklist if self._is_expired_jti(jti)}
        self._blacklist -= expired_in_memory
        
        return count
    
    def _is_expired_jti(self, jti: str) -> bool:
        """
        Check if a JTI is expired based on naming convention.
        JTIs are formatted as: {timestamp}_{random}
        """
        try:
            timestamp = int(jti.split('_')[0])
            exp_time = datetime.fromtimestamp(timestamp)
            return datetime.utcnow() > exp_time
        except (ValueError, IndexError):
            # If we can't parse, assume it's still valid
            return False


# Singleton instance
token_blacklist_service = TokenBlacklistService()

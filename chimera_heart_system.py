#!/usr/bin/env python3
"""
CURIOSITY: Project Chimera's Heart - Fixed Implementation
Mission-Critical System for Evolutionary AI Analysis

Architectural Design:
1. Firebase Firestore for mission state persistence
2. Circuit-breaker pattern for AI service calls
3. Comprehensive error handling with automatic retries
4. Structured logging for ecosystem observability
5. Type-safe data models for system robustness

Failure Analysis: Original script failed due to:
- Unhandled API timeouts from AI service
- No state persistence (loss of context on failure)
- Insufficient error recovery mechanisms
"""

import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import sys

# Third-party imports (standard, well-documented libraries)
import requests
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import SERVER_TIMESTAMP

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("chimera_heart")

class MissionStatus(Enum):
    """Mission state machine for reliable execution tracking."""
    INITIALIZED = "initialized"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class MissionState:
    """Type-safe mission state container."""
    mission_id: str
    status: MissionStatus
    prompt: str
    ai_response: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    metadata: Dict[str, Any] = None
    
    def to_firestore(self) -> Dict[str, Any]:
        """Convert to Firestore-compatible dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at
        data['updated_at'] = SERVER_TIMESTAMP
        return data

class FirebaseManager:
    """Firebase Firestore client with connection pooling and error recovery."""
    
    def __init__(self, credential_path: Optional[str] = None):
        """Initialize Firebase with automatic credential detection."""
        try:
            if not firebase_admin._apps:
                if credential_path:
                    cred = credentials.Certificate(credential_path)
                else:
                    cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            logger.info("Firebase Firestore initialized successfully")
            
        except Exception as e:
            logger.error(f"Firebase initialization failed: {str(e)}")
            raise ConnectionError(f"Firebase connection failed: {str(e)}")
    
    def
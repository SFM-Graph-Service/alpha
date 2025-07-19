"""
Transaction Management for SFM Service

This module provides transaction support for SFM operations, allowing
atomic operations with rollback capabilities on failure.

Features:
- Context manager for transactional operations
- Rollback support for failed operations
- Operation tracking and state management
- Nested transaction support
- Performance monitoring integration
"""

import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionStatus(Enum):
    """Transaction execution status."""
    PENDING = "pending"
    ACTIVE = "active"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class OperationRecord:
    """Record of an operation performed within a transaction."""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = ""
    operation_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    rollback_data: Optional[Dict[str, Any]] = None
    rollback_function: Optional[Callable] = None


@dataclass
class Transaction:
    """Transaction context with operations tracking."""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TransactionStatus = TransactionStatus.PENDING
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    operations: List[OperationRecord] = field(default_factory=list)
    error: Optional[Exception] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_operation(self, operation_type: str, data: Dict[str, Any], 
                     rollback_data: Optional[Dict[str, Any]] = None,
                     rollback_function: Optional[Callable] = None) -> str:
        """Add an operation to the transaction."""
        operation = OperationRecord(
            operation_type=operation_type,
            operation_data=data,
            rollback_data=rollback_data,
            rollback_function=rollback_function
        )
        self.operations.append(operation)
        logger.debug(f"Added operation {operation_type} to transaction {self.transaction_id}")
        return operation.operation_id
    
    def duration(self) -> float:
        """Get transaction duration in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time


class TransactionManager:
    """Manages transactions for SFM operations."""
    
    def __init__(self):
        self._active_transactions: Dict[str, Transaction] = {}
        self._transaction_history: List[Transaction] = []
        self._current_transaction: Optional[Transaction] = None
    
    @contextmanager
    def transaction(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Context manager for transactional operations.
        
        Args:
            metadata: Optional metadata for the transaction
            
        Yields:
            TransactionManager: The transaction manager instance
            
        Raises:
            Exception: Re-raises any exception that occurred during transaction
        """
        transaction = Transaction(
            metadata=metadata or {},
            status=TransactionStatus.ACTIVE
        )
        
        self._active_transactions[transaction.transaction_id] = transaction
        old_transaction = self._current_transaction
        self._current_transaction = transaction
        
        logger.info(f"Starting transaction {transaction.transaction_id}")
        
        try:
            yield self
            
            # If we reach here, commit the transaction
            self._commit_transaction(transaction)
            logger.info(f"Transaction {transaction.transaction_id} committed successfully")
            
        except Exception as e:
            # Rollback on any exception
            transaction.error = e
            self._rollback_transaction(transaction)
            logger.error(f"Transaction {transaction.transaction_id} failed and rolled back: {e}")
            raise
            
        finally:
            # Clean up
            transaction.end_time = time.time()
            self._current_transaction = old_transaction
            if transaction.transaction_id in self._active_transactions:
                del self._active_transactions[transaction.transaction_id]
            self._transaction_history.append(transaction)
            
            # Keep history limited to prevent memory issues
            if len(self._transaction_history) > 1000:
                self._transaction_history = self._transaction_history[-500:]
    
    def add_operation(self, operation_type: str, data: Dict[str, Any],
                     rollback_data: Optional[Dict[str, Any]] = None,
                     rollback_function: Optional[Callable] = None) -> Optional[str]:
        """
        Add an operation to the current transaction.
        
        Args:
            operation_type: Type of operation being performed
            data: Operation data
            rollback_data: Data needed for rollback
            rollback_function: Function to call for rollback
            
        Returns:
            Operation ID if in transaction, None otherwise
        """
        if self._current_transaction:
            return self._current_transaction.add_operation(
                operation_type, data, rollback_data, rollback_function
            )
        return None
    
    def _commit_transaction(self, transaction: Transaction):
        """Commit a transaction."""
        transaction.status = TransactionStatus.COMMITTED
        logger.debug(f"Committed transaction {transaction.transaction_id} "
                    f"with {len(transaction.operations)} operations")
    
    def _rollback_transaction(self, transaction: Transaction):
        """Rollback a transaction by reversing operations."""
        transaction.status = TransactionStatus.ROLLED_BACK
        
        # Rollback operations in reverse order
        for operation in reversed(transaction.operations):
            try:
                if operation.rollback_function:
                    logger.debug(f"Rolling back operation {operation.operation_type}")
                    operation.rollback_function(operation.rollback_data)
                else:
                    logger.warning(f"No rollback function for operation {operation.operation_type}")
            except Exception as rollback_error:
                logger.error(f"Rollback failed for operation {operation.operation_type}: {rollback_error}")
                # Continue with other rollbacks even if one fails
        
        logger.info(f"Rolled back transaction {transaction.transaction_id}")
    
    def get_transaction_stats(self) -> Dict[str, Any]:
        """Get transaction statistics."""
        total_transactions = len(self._transaction_history)
        if total_transactions == 0:
            return {
                "total_transactions": 0,
                "committed_transactions": 0,
                "rolled_back_transactions": 0,
                "average_duration": 0.0,
                "active_transactions": 0
            }
        
        committed = sum(1 for t in self._transaction_history 
                       if t.status == TransactionStatus.COMMITTED)
        rolled_back = sum(1 for t in self._transaction_history 
                         if t.status == TransactionStatus.ROLLED_BACK)
        avg_duration = sum(t.duration() for t in self._transaction_history) / total_transactions
        
        return {
            "total_transactions": total_transactions,
            "committed_transactions": committed,
            "rolled_back_transactions": rolled_back,
            "average_duration": avg_duration,
            "active_transactions": len(self._active_transactions)
        }
    
    def get_current_transaction_id(self) -> Optional[str]:
        """Get the current transaction ID if any."""
        return self._current_transaction.transaction_id if self._current_transaction else None
    
    def is_in_transaction(self) -> bool:
        """Check if currently in a transaction."""
        return self._current_transaction is not None
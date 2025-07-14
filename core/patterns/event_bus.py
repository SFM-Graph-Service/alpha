"""
Event Bus Implementation for SFM Framework

This module implements an event-driven architecture pattern using an Event Bus
to enable loose coupling between components through asynchronous event handling.
"""

import uuid
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Set, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for ordering event processing."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Event:
    """
    Base event class for the event bus system.
    
    Events carry information about what happened and provide context
    for event handlers to process.
    """
    event_type: str
    data: Dict[str, Any]
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None
    priority: EventPriority = EventPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate event data after initialization."""
        if not self.event_type:
            raise ValueError("event_type cannot be empty")
        if not isinstance(self.data, dict):
            raise ValueError("data must be a dictionary")


@dataclass
class EventHandlerMetadata:
    """Metadata about an event handler."""
    handler_id: str
    event_type: str
    handler_function: Callable
    priority: int
    is_async: bool
    created_at: datetime
    call_count: int = 0
    error_count: int = 0
    last_called: Optional[datetime] = None
    last_error: Optional[str] = None
    processing_time_ms: float = 0.0


class EventHandler(ABC):
    """Abstract base class for event handlers."""
    
    @abstractmethod
    def handle(self, event: Event) -> None:
        """Handle an event synchronously."""
        pass
    
    async def handle_async(self, event: Event) -> None:
        """Handle an event asynchronously (default implementation calls handle)."""
        self.handle(event)
    
    def get_handler_id(self) -> str:
        """Get a unique identifier for this handler."""
        return f"{self.__class__.__name__}_{id(self)}"
    
    def get_supported_event_types(self) -> List[str]:
        """Get list of event types this handler supports."""
        return []
    
    def get_priority(self) -> int:
        """Get the priority of this handler (higher numbers = higher priority)."""
        return 0


class AsyncEventHandler(EventHandler):
    """Abstract base class for asynchronous event handlers."""
    
    def handle(self, event: Event) -> None:
        """Synchronous handle method - not implemented for async handlers."""
        raise NotImplementedError("Async handlers should implement handle_async")
    
    @abstractmethod
    async def handle_async(self, event: Event) -> None:
        """Handle an event asynchronously."""
        pass


class EventBus:
    """
    Event bus for decoupled communication between components.
    
    The event bus allows components to publish events and subscribe to events
    without direct dependencies on each other.
    """
    
    def __init__(self, max_event_history: int = 1000):
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._handler_metadata: Dict[str, EventHandlerMetadata] = {}
        self._event_history: List[Event] = []
        self._max_event_history = max_event_history
        self._wildcard_handlers: List[EventHandler] = []
        self._middleware: List[Callable[[Event], Union[Event, None]]] = []
        self._error_handlers: List[Callable[[Exception, Event, EventHandler], None]] = []
        self._filters: List[Callable[[Event], bool]] = []
        self._is_processing = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._metrics = {
            "events_published": 0,
            "events_processed": 0,
            "events_failed": 0,
            "handlers_registered": 0,
            "handlers_removed": 0
        }
    
    def subscribe(self, event_type: str, handler: EventHandler, priority: int = 0) -> str:
        """
        Subscribe a handler to an event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The handler to invoke when the event occurs
            priority: Handler priority (higher numbers execute first)
            
        Returns:
            Handler ID for later removal
        """
        handler_id = handler.get_handler_id()
        
        # Check if handler is already registered for this event type
        if any(h.get_handler_id() == handler_id for h in self._handlers[event_type]):
            logger.warning(f"Handler {handler_id} already registered for event type {event_type}")
            return handler_id
        
        # Add handler to the list
        self._handlers[event_type].append(handler)
        
        # Sort handlers by priority (higher priority first)
        self._handlers[event_type].sort(key=lambda h: h.get_priority(), reverse=True)
        
        # Store metadata
        self._handler_metadata[handler_id] = EventHandlerMetadata(
            handler_id=handler_id,
            event_type=event_type,
            handler_function=handler.handle,
            priority=priority,
            is_async=isinstance(handler, AsyncEventHandler),
            created_at=datetime.now()
        )
        
        self._metrics["handlers_registered"] += 1
        
        logger.debug(f"Registered handler {handler_id} for event type {event_type}")
        return handler_id
    
    def subscribe_to_all(self, handler: EventHandler) -> str:
        """
        Subscribe a handler to all events (wildcard subscription).
        
        Args:
            handler: The handler to invoke for all events
            
        Returns:
            Handler ID for later removal
        """
        handler_id = handler.get_handler_id()
        
        if handler not in self._wildcard_handlers:
            self._wildcard_handlers.append(handler)
            
            # Store metadata
            self._handler_metadata[handler_id] = EventHandlerMetadata(
                handler_id=handler_id,
                event_type="*",
                handler_function=handler.handle,
                priority=handler.get_priority(),
                is_async=isinstance(handler, AsyncEventHandler),
                created_at=datetime.now()
            )
            
            self._metrics["handlers_registered"] += 1
            logger.debug(f"Registered wildcard handler {handler_id}")
        
        return handler_id
    
    def unsubscribe(self, event_type: str, handler_id: str) -> bool:
        """
        Unsubscribe a handler from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            handler_id: The ID of the handler to remove
            
        Returns:
            True if handler was found and removed, False otherwise
        """
        if event_type == "*":
            # Remove from wildcard handlers
            for handler in self._wildcard_handlers:
                if handler.get_handler_id() == handler_id:
                    self._wildcard_handlers.remove(handler)
                    if handler_id in self._handler_metadata:
                        del self._handler_metadata[handler_id]
                    self._metrics["handlers_removed"] += 1
                    logger.debug(f"Removed wildcard handler {handler_id}")
                    return True
            return False
        
        # Remove from specific event type handlers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                if handler.get_handler_id() == handler_id:
                    self._handlers[event_type].remove(handler)
                    if handler_id in self._handler_metadata:
                        del self._handler_metadata[handler_id]
                    self._metrics["handlers_removed"] += 1
                    logger.debug(f"Removed handler {handler_id} from event type {event_type}")
                    return True
        
        return False
    
    def publish(self, event: Event) -> None:
        """
        Publish an event to all registered handlers.
        
        Args:
            event: The event to publish
        """
        # Apply filters
        if not self._apply_filters(event):
            logger.debug(f"Event {event.event_id} filtered out")
            return
        
        # Apply middleware
        processed_event = self._apply_middleware(event)
        if processed_event is None:
            logger.debug(f"Event {event.event_id} consumed by middleware")
            return
        
        # Add to history
        self._add_to_history(processed_event)
        
        # Process event
        self._process_event_sync(processed_event)
        
        self._metrics["events_published"] += 1
        logger.debug(f"Published event {event.event_type} with ID {event.event_id}")
    
    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.
        
        Args:
            event: The event to publish
        """
        await self._event_queue.put(event)
    
    async def start_async_processing(self) -> None:
        """Start processing events asynchronously."""
        self._is_processing = True
        
        while self._is_processing:
            try:
                event = await self._event_queue.get()
                
                # Apply filters
                if not self._apply_filters(event):
                    continue
                
                # Apply middleware
                processed_event = self._apply_middleware(event)
                if processed_event is None:
                    continue
                
                # Add to history
                self._add_to_history(processed_event)
                
                # Process event asynchronously
                await self._process_event_async(processed_event)
                
                self._metrics["events_published"] += 1
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                self._metrics["events_failed"] += 1
    
    def stop_async_processing(self) -> None:
        """Stop asynchronous event processing."""
        self._is_processing = False
    
    def _process_event_sync(self, event: Event) -> None:
        """Process an event synchronously."""
        handlers = self._get_handlers_for_event(event)
        
        for handler in handlers:
            try:
                start_time = datetime.now()
                
                if isinstance(handler, AsyncEventHandler):
                    # Skip async handlers in sync processing
                    continue
                
                handler.handle(event)
                
                # Update metadata
                self._update_handler_metadata(handler, None, start_time)
                
            except Exception as e:
                logger.error(f"Error in handler {handler.get_handler_id()}: {e}")
                self._handle_error(e, event, handler)
                self._update_handler_metadata(handler, e, start_time)
    
    async def _process_event_async(self, event: Event) -> None:
        """Process an event asynchronously."""
        handlers = self._get_handlers_for_event(event)
        
        # Process async handlers
        async_tasks = []
        for handler in handlers:
            if isinstance(handler, AsyncEventHandler):
                async_tasks.append(self._handle_async_event(handler, event))
        
        # Process sync handlers
        sync_tasks = []
        for handler in handlers:
            if not isinstance(handler, AsyncEventHandler):
                sync_tasks.append(self._handle_sync_event_in_async(handler, event))
        
        # Wait for all handlers to complete
        all_tasks = async_tasks + sync_tasks
        if all_tasks:
            await asyncio.gather(*all_tasks, return_exceptions=True)
    
    async def _handle_async_event(self, handler: AsyncEventHandler, event: Event) -> None:
        """Handle an event with an async handler."""
        try:
            start_time = datetime.now()
            await handler.handle_async(event)
            self._update_handler_metadata(handler, None, start_time)
        except Exception as e:
            logger.error(f"Error in async handler {handler.get_handler_id()}: {e}")
            self._handle_error(e, event, handler)
            self._update_handler_metadata(handler, e, start_time)
    
    async def _handle_sync_event_in_async(self, handler: EventHandler, event: Event) -> None:
        """Handle an event with a sync handler in async context."""
        try:
            start_time = datetime.now()
            # Run sync handler in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, handler.handle, event)
            self._update_handler_metadata(handler, None, start_time)
        except Exception as e:
            logger.error(f"Error in sync handler {handler.get_handler_id()}: {e}")
            self._handle_error(e, event, handler)
            self._update_handler_metadata(handler, e, start_time)
    
    def _get_handlers_for_event(self, event: Event) -> List[EventHandler]:
        """Get all handlers that should process this event."""
        handlers = []
        
        # Add specific handlers
        if event.event_type in self._handlers:
            handlers.extend(self._handlers[event.event_type])
        
        # Add wildcard handlers
        handlers.extend(self._wildcard_handlers)
        
        # Sort by priority
        handlers.sort(key=lambda h: h.get_priority(), reverse=True)
        
        return handlers
    
    def _apply_filters(self, event: Event) -> bool:
        """Apply filters to determine if event should be processed."""
        for filter_func in self._filters:
            try:
                if not filter_func(event):
                    return False
            except Exception as e:
                logger.error(f"Error in event filter: {e}")
        return True
    
    def _apply_middleware(self, event: Event) -> Optional[Event]:
        """Apply middleware to transform or filter events."""
        current_event = event
        
        for middleware in self._middleware:
            try:
                current_event = middleware(current_event)
                if current_event is None:
                    return None
            except Exception as e:
                logger.error(f"Error in middleware: {e}")
                return None
        
        return current_event
    
    def _handle_error(self, error: Exception, event: Event, handler: EventHandler) -> None:
        """Handle errors from event handlers."""
        self._metrics["events_failed"] += 1
        
        for error_handler in self._error_handlers:
            try:
                error_handler(error, event, handler)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
    
    def _update_handler_metadata(self, handler: EventHandler, error: Optional[Exception], start_time: datetime) -> None:
        """Update handler metadata with execution information."""
        handler_id = handler.get_handler_id()
        
        if handler_id in self._handler_metadata:
            metadata = self._handler_metadata[handler_id]
            metadata.call_count += 1
            metadata.last_called = datetime.now()
            metadata.processing_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            if error:
                metadata.error_count += 1
                metadata.last_error = str(error)
    
    def _add_to_history(self, event: Event) -> None:
        """Add event to history with size limit."""
        self._event_history.append(event)
        
        if len(self._event_history) > self._max_event_history:
            self._event_history = self._event_history[-self._max_event_history:]
    
    def add_middleware(self, middleware: Callable[[Event], Union[Event, None]]) -> None:
        """Add middleware to process events before they reach handlers."""
        self._middleware.append(middleware)
    
    def add_error_handler(self, error_handler: Callable[[Exception, Event, EventHandler], None]) -> None:
        """Add error handler to process exceptions from event handlers."""
        self._error_handlers.append(error_handler)
    
    def add_filter(self, filter_func: Callable[[Event], bool]) -> None:
        """Add filter to determine which events should be processed."""
        self._filters.append(filter_func)
    
    def get_event_history(self, limit: Optional[int] = None) -> List[Event]:
        """Get event history."""
        if limit is None:
            return self._event_history.copy()
        return self._event_history[-limit:]
    
    def get_handler_metadata(self, handler_id: Optional[str] = None) -> Union[EventHandlerMetadata, List[EventHandlerMetadata]]:
        """Get metadata for handlers."""
        if handler_id is not None:
            return self._handler_metadata.get(handler_id)
        return list(self._handler_metadata.values())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics."""
        return {
            **self._metrics,
            "active_handlers": len(self._handler_metadata),
            "event_history_size": len(self._event_history),
            "wildcard_handlers": len(self._wildcard_handlers),
            "middleware_count": len(self._middleware),
            "error_handlers": len(self._error_handlers),
            "filters": len(self._filters)
        }
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
    
    def clear_handlers(self) -> None:
        """Clear all handlers."""
        self._handlers.clear()
        self._wildcard_handlers.clear()
        self._handler_metadata.clear()
        self._metrics["handlers_registered"] = 0
        self._metrics["handlers_removed"] = 0
    
    def get_supported_event_types(self) -> Set[str]:
        """Get all event types that have registered handlers."""
        return set(self._handlers.keys())


# Example Event Handlers

class LoggingEventHandler(EventHandler):
    """Example handler that logs all events."""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = log_level
    
    def handle(self, event: Event) -> None:
        """Log the event."""
        logger.info(f"Event {event.event_type} at {event.timestamp}: {event.data}")
    
    def get_supported_event_types(self) -> List[str]:
        """This handler supports all event types."""
        return ["*"]


class MetricsEventHandler(EventHandler):
    """Example handler that tracks event metrics."""
    
    def __init__(self):
        self.event_counts: Dict[str, int] = defaultdict(int)
        self.last_event_time: Dict[str, datetime] = {}
    
    def handle(self, event: Event) -> None:
        """Track event metrics."""
        self.event_counts[event.event_type] += 1
        self.last_event_time[event.event_type] = event.timestamp
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        return {
            "event_counts": dict(self.event_counts),
            "last_event_times": {k: v.isoformat() for k, v in self.last_event_time.items()}
        }


class CacheInvalidationHandler(EventHandler):
    """Example handler that invalidates caches based on events."""
    
    def __init__(self):
        self.invalidated_keys: List[str] = []
    
    def handle(self, event: Event) -> None:
        """Invalidate caches based on event type."""
        if event.event_type in ["node_added", "node_removed", "node_updated"]:
            cache_key = f"node_{event.data.get('node_id')}"
            self.invalidated_keys.append(cache_key)
        elif event.event_type in ["relationship_added", "relationship_removed"]:
            cache_key = "graph_structure"
            self.invalidated_keys.append(cache_key)
    
    def get_supported_event_types(self) -> List[str]:
        """Supported event types for cache invalidation."""
        return ["node_added", "node_removed", "node_updated", "relationship_added", "relationship_removed"]


# Example middleware functions
def event_enrichment_middleware(event: Event) -> Event:
    """Middleware that enriches events with additional metadata."""
    event.metadata["processed_at"] = datetime.now().isoformat()
    event.metadata["process_id"] = "event_bus"
    return event


def event_filtering_middleware(event: Event) -> Optional[Event]:
    """Middleware that filters out certain events."""
    # Example: filter out events with empty data
    if not event.data:
        return None
    return event


def event_transformation_middleware(event: Event) -> Event:
    """Middleware that transforms event data."""
    # Example: normalize event type to lowercase
    event.event_type = event.event_type.lower()
    return event


# Global event bus instance
_global_event_bus = EventBus()


def get_global_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _global_event_bus


def publish_event(event_type: str, data: Dict[str, Any], **kwargs) -> None:
    """Convenience function to publish an event to the global event bus."""
    event = Event(event_type=event_type, data=data, **kwargs)
    _global_event_bus.publish(event)


def subscribe_to_event(event_type: str, handler: EventHandler, priority: int = 0) -> str:
    """Convenience function to subscribe to an event on the global event bus."""
    return _global_event_bus.subscribe(event_type, handler, priority)
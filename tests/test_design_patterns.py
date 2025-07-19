"""
Tests for Design Patterns Implementation

This module tests the various design patterns implemented for the SFM framework.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, MagicMock

from utils.patterns.observer import (
    GraphChangeObserver, GraphObservable, CachingObserver, MetricsObserver
)
from utils.patterns.command import (
    Command, CommandManager, AddNodeCommand, RemoveNodeCommand,
    AddRelationshipCommand, MacroCommand
)
from utils.patterns.strategy import (
    CentralityStrategy, BetweennessCentralityStrategy, EigenvectorCentralityStrategy,
    StrategyManager, CentralityAnalyzer
)
from utils.patterns.decorator import (
    ValidationDecorator, CacheDecorator, AuditDecorator, ValidationError,
    cache_result, audit_operation, validate_inputs
)
from utils.patterns.event_bus import (
    Event, EventHandler, EventBus, LoggingEventHandler, MetricsEventHandler
)
from utils.patterns.dependency_injection import (
    DIContainer, LifecycleType, ServiceScope, InjectionError, CircularDependencyError
)

from models.base_nodes import Node
from models.relationships import Relationship
from models.sfm_enums import RelationshipKind


class TestObserverPattern:
    """Test the Observer pattern implementation."""
    
    def test_observer_notifications(self):
        """Test that observers are notified of graph changes."""
        # Create observable and observer
        observable = GraphObservable()
        observer = Mock(spec=GraphChangeObserver)
        
        # Add observer
        observable.add_observer(observer)
        
        # Create test node
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        node.label = "Test Node"
        
        # Notify of node addition
        observable._notify_node_added(node)
        
        # Verify observer was called
        observer.on_node_added.assert_called_once_with(node)
    
    def test_observer_removal(self):
        """Test that observers can be removed."""
        observable = GraphObservable()
        observer = Mock(spec=GraphChangeObserver)
        
        observable.add_observer(observer)
        observable.remove_observer(observer)
        
        # Create test node and notify
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        observable._notify_node_added(node)
        
        # Observer should not be called
        observer.on_node_added.assert_not_called()
    
    def test_change_history(self):
        """Test that change history is maintained."""
        observable = GraphObservable()
        
        # Create test node
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        node.label = "Test Node"
        
        # Notify of changes
        observable._notify_node_added(node)
        observable._notify_node_removed(node.id)
        
        # Check history
        history = observable.get_change_history()
        assert len(history) == 2
        assert history[0]["change_type"] == "node_added"
        assert history[1]["change_type"] == "node_removed"
    
    def test_caching_observer(self):
        """Test the caching observer functionality."""
        observer = CachingObserver()
        
        # Create test node
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        node.label = "Test Node"
        
        # Notify of node addition
        observer.on_node_added(node)
        
        # Check that caches were invalidated
        invalidated = observer.get_invalidated_caches()
        assert f"node_cache_{node.id}" in invalidated
        assert "node_list_cache" in invalidated
    
    def test_metrics_observer(self):
        """Test the metrics observer functionality."""
        observer = MetricsObserver()
        
        # Create test node
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        
        # Notify of node addition
        observer.on_node_added(node)
        
        # Check metrics
        metrics = observer.get_metrics()
        assert metrics["nodes_added"] == 1
        assert metrics["last_change_timestamp"] is not None


class TestCommandPattern:
    """Test the Command pattern implementation."""
    
    def test_command_execution(self):
        """Test basic command execution."""
        # Create mock graph
        graph = Mock()
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        node.label = "Test Node"
        
        # Create and execute command
        command = AddNodeCommand(graph, node)
        command.execute()
        
        # Verify command was executed
        graph.add_node.assert_called_once_with(node)
        assert command.executed
    
    def test_command_undo(self):
        """Test command undo functionality."""
        # Create mock graph with node registry
        graph = Mock()
        graph._node_registry = Mock()
        graph._node_registry.get_collection_name.return_value = "test_collection"
        
        # Create mock collection
        collection = {}
        setattr(graph, "test_collection", collection)
        
        # Create mock node index
        node_index = {}
        graph._node_index = node_index
        
        # Create node
        node = Mock(spec=Node)
        node.id = uuid.uuid4()
        node.label = "Test Node"
        
        # Create and execute command
        command = AddNodeCommand(graph, node)
        command.execute()
        
        # Simulate node being added to collection and index
        collection[node.id] = node
        node_index[node.id] = node
        
        # Undo command
        assert command.can_undo()
        command.undo()
        
        # Verify node was removed
        assert node.id not in collection
        assert command.undone
    
    def test_command_manager(self):
        """Test command manager functionality."""
        manager = CommandManager()
        
        # Create mock command
        command = Mock(spec=Command)
        command.command_id = uuid.uuid4()
        command.timestamp = datetime.now()
        command.executed = False
        command.undone = False
        command.execute.return_value = "result"
        command.can_undo.return_value = True
        command.undo.return_value = True
        command.get_description.return_value = "Test command"
        
        # Execute command
        result = manager.execute(command)
        
        # Verify command was executed
        command.execute.assert_called_once()
        assert result == "result"
        assert manager.can_undo()
        
        # Undo command
        success = manager.undo()
        assert success
        command.undo.assert_called_once()
    
    def test_macro_command(self):
        """Test macro command functionality."""
        # Create mock commands
        cmd1 = Mock(spec=Command)
        cmd1.execute.return_value = "result1"
        cmd1.can_undo.return_value = True
        cmd1.undo.return_value = True
        
        cmd2 = Mock(spec=Command)
        cmd2.execute.return_value = "result2"
        cmd2.can_undo.return_value = True
        cmd2.undo.return_value = True
        
        # Create macro command
        macro = MacroCommand([cmd1, cmd2], "Test macro")
        
        # Execute macro
        results = macro.execute()
        
        # Verify all commands were executed
        cmd1.execute.assert_called_once()
        cmd2.execute.assert_called_once()
        assert results == ["result1", "result2"]
        assert macro.executed
        
        # Undo macro
        success = macro.undo()
        assert success
        cmd1.undo.assert_called_once()
        cmd2.undo.assert_called_once()


class TestStrategyPattern:
    """Test the Strategy pattern implementation."""
    
    def test_centrality_strategy(self):
        """Test centrality strategy functionality."""
        import networkx as nx
        
        # Create test graph
        graph = nx.Graph()
        node1 = uuid.uuid4()
        node2 = uuid.uuid4()
        node3 = uuid.uuid4()
        
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_node(node3)
        graph.add_edge(node1, node2)
        graph.add_edge(node2, node3)
        
        # Test betweenness centrality strategy
        strategy = BetweennessCentralityStrategy()
        assert strategy.get_name() == "betweenness"
        
        centrality = strategy.calculate(graph, node2)
        assert centrality > 0  # node2 should have high betweenness centrality
        
        all_centralities = strategy.calculate_all(graph)
        assert len(all_centralities) == 3
        assert all(isinstance(score, float) for score in all_centralities.values())
    
    def test_strategy_manager(self):
        """Test strategy manager functionality."""
        manager = StrategyManager()
        
        # Test that default strategies are registered
        centrality_strategies = manager.list_strategies("centrality")
        assert "centrality" in centrality_strategies
        assert "betweenness" in centrality_strategies["centrality"]
        
        # Test getting strategy
        strategy = manager.get_strategy("centrality", "betweenness")
        assert strategy is not None
        assert isinstance(strategy, BetweennessCentralityStrategy)
        
        # Test default strategy
        default_strategy = manager.get_default_strategy("centrality")
        assert default_strategy == "betweenness"
    
    def test_centrality_analyzer(self):
        """Test centrality analyzer functionality."""
        import networkx as nx
        
        analyzer = CentralityAnalyzer()
        
        # Create test graph
        graph = nx.Graph()
        node1 = uuid.uuid4()
        node2 = uuid.uuid4()
        graph.add_node(node1)
        graph.add_node(node2)
        graph.add_edge(node1, node2)
        
        # Test centrality calculation
        centrality = analyzer.calculate_centrality(graph, node1)
        assert isinstance(centrality, float)
        
        # Test all centralities
        all_centralities = analyzer.calculate_all_centralities(graph)
        assert len(all_centralities) == 2
        
        # Test available strategies
        strategies = analyzer.get_available_strategies()
        assert "betweenness" in strategies
        assert "closeness" in strategies


class TestDecoratorPattern:
    """Test the Decorator pattern implementation."""
    
    def test_validation_decorator(self):
        """Test validation decorator functionality."""
        # Create validator
        def validate_positive(value):
            return value > 0
        
        # Create decorated function
        @validate_inputs(lambda value: validate_positive(value))
        def process_value(value):
            return value * 2
        
        # Test valid input
        result = process_value(5)
        assert result == 10
        
        # Test invalid input
        with pytest.raises(ValidationError):
            process_value(-1)
    
    def test_cache_decorator(self):
        """Test cache decorator functionality."""
        call_count = 0
        
        @cache_result(ttl=60)
        def expensive_function(value):
            nonlocal call_count
            call_count += 1
            return value * 2
        
        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call (should be cached)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should still be 1 due to caching
        
        # Different argument (should not be cached)
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_audit_decorator(self):
        """Test audit decorator functionality."""
        from utils.patterns.decorator import AuditLogger, AuditLevel
        
        audit_logger = AuditLogger()
        
        @audit_operation(AuditLevel.INFO, audit_logger)
        def test_function(value):
            return value * 2
        
        # Call function
        result = test_function(5)
        assert result == 10
        
        # Check audit log
        entries = audit_logger.get_entries()
        assert len(entries) == 1
        assert entries[0].operation == "test_function"
        assert entries[0].level == AuditLevel.INFO
        assert entries[0].result == 10


class TestEventBus:
    """Test the Event Bus implementation."""
    
    def test_event_creation(self):
        """Test event creation and validation."""
        event = Event("test_event", {"key": "value"})
        
        assert event.event_type == "test_event"
        assert event.data == {"key": "value"}
        assert event.event_id is not None
        assert event.timestamp is not None
    
    def test_event_subscription(self):
        """Test event subscription and handling."""
        bus = EventBus()
        handler = Mock(spec=EventHandler)
        handler.get_handler_id.return_value = "test_handler"
        handler.get_priority.return_value = 0
        
        # Subscribe handler
        handler_id = bus.subscribe("test_event", handler)
        assert handler_id == "test_handler"
        
        # Publish event
        event = Event("test_event", {"key": "value"})
        bus.publish(event)
        
        # Verify handler was called
        handler.handle.assert_called_once_with(event)
    
    def test_wildcard_subscription(self):
        """Test wildcard event subscription."""
        bus = EventBus()
        handler = Mock(spec=EventHandler)
        handler.get_handler_id.return_value = "wildcard_handler"
        handler.get_priority.return_value = 0
        
        # Subscribe to all events
        handler_id = bus.subscribe_to_all(handler)
        assert handler_id == "wildcard_handler"
        
        # Publish different events
        event1 = Event("event1", {"key": "value1"})
        event2 = Event("event2", {"key": "value2"})
        
        bus.publish(event1)
        bus.publish(event2)
        
        # Verify handler was called for both events
        assert handler.handle.call_count == 2
    
    def test_event_unsubscription(self):
        """Test event unsubscription."""
        bus = EventBus()
        handler = Mock(spec=EventHandler)
        handler.get_handler_id.return_value = "test_handler"
        handler.get_priority.return_value = 0
        
        # Subscribe and then unsubscribe
        handler_id = bus.subscribe("test_event", handler)
        success = bus.unsubscribe("test_event", handler_id)
        assert success
        
        # Publish event
        event = Event("test_event", {"key": "value"})
        bus.publish(event)
        
        # Handler should not be called
        handler.handle.assert_not_called()
    
    def test_event_history(self):
        """Test event history functionality."""
        bus = EventBus()
        
        # Publish events
        event1 = Event("event1", {"key": "value1"})
        event2 = Event("event2", {"key": "value2"})
        
        bus.publish(event1)
        bus.publish(event2)
        
        # Check history
        history = bus.get_event_history()
        assert len(history) == 2
        assert history[0].event_type == "event1"
        assert history[1].event_type == "event2"


class TestDependencyInjection:
    """Test the Dependency Injection implementation."""
    
    def test_singleton_registration(self):
        """Test singleton service registration."""
        container = DIContainer()
        
        # Register singleton
        instance = "test_singleton"
        container.register_singleton(str, instance)
        
        # Get service
        service = container.get(str)
        assert service == instance
        
        # Get again - should be same instance
        service2 = container.get(str)
        assert service2 is service
    
    def test_transient_registration(self):
        """Test transient service registration."""
        container = DIContainer()
        
        # Register transient service
        container.register_transient(list)
        
        # Get service multiple times
        service1 = container.get(list)
        service2 = container.get(list)
        
        # Should be different instances
        assert service1 is not service2
        assert isinstance(service1, list)
        assert isinstance(service2, list)
    
    def test_factory_registration(self):
        """Test factory service registration."""
        container = DIContainer()
        
        # Register factory
        def create_dict():
            return {"created": True}
        
        container.register_factory(dict, create_dict)
        
        # Get service
        service = container.get(dict)
        assert service == {"created": True}
    
    def test_scoped_services(self):
        """Test scoped service functionality."""
        container = DIContainer()
        container.register_scoped(list)
        
        # Create scope
        with container.scope() as scope:
            service1 = scope.get_service(list)
            service2 = scope.get_service(list)
            
            # Should be same instance within scope
            assert service1 is service2
        
        # Create new scope
        with container.scope() as scope:
            service3 = scope.get_service(list)
            
            # Should be different instance in new scope
            assert service3 is not service1
    
    def test_dependency_injection(self):
        """Test automatic dependency injection."""
        container = DIContainer()
        
        # Define services with dependencies
        class ServiceA:
            def __init__(self):
                self.name = "A"
        
        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a
                self.name = "B"
        
        # Register services
        container.register_singleton(ServiceA, ServiceA())
        container.register_transient(ServiceB)
        
        # Get service with dependency
        service_b = container.get(ServiceB)
        assert service_b.name == "B"
        assert service_b.service_a.name == "A"
    
    def test_circular_dependency_detection(self):
        """Test circular dependency detection."""
        container = DIContainer()
        
        # Register a service
        container.register_transient(str)
        
        # Simulate circular dependency by manually setting up creation stack
        container._creation_stack = [str]  # Simulate str is being created
        
        # Try to get str again - should raise circular dependency error
        with pytest.raises(CircularDependencyError):
            container._get_service(str)  # This should detect the circular dependency


if __name__ == "__main__":
    pytest.main([__file__])
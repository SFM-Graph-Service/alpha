#!/usr/bin/env python3
"""
Comprehensive demonstration of the design patterns implemented in the SFM framework.

This script showcases all the major design patterns working together:
- Observer Pattern for graph change notifications
- Command Pattern for undo/redo operations
- Strategy Pattern for pluggable algorithms
- Decorator Pattern for cross-cutting concerns
- Event Bus for loose coupling
- Plugin Architecture for extensibility
- Dependency Injection for testability

Usage: python examples/design_patterns_demo.py
"""

import uuid
import time
from datetime import datetime
from typing import Dict, Any

# Core SFM imports
from core.graph import SFMGraph
from core.core_nodes import Actor, Institution, Resource
from core.relationships import Relationship
from core.sfm_enums import RelationshipKind, ResourceType
from core.sfm_query import NetworkXSFMQueryEngine

# Design pattern imports
from core.patterns.observer import (
    MetricsObserver, CachingObserver, GraphChangeObserver
)
from core.patterns.command import (
    CommandManager, AddNodeCommand, AddRelationshipCommand, MacroCommand
)
from core.patterns.strategy import StrategyManager, CentralityAnalyzer
from core.patterns.decorator import (
    cache_result, audit_operation, validate_inputs,
    AuditLevel, ValidationError
)
from core.patterns.event_bus import (
    EventBus, Event, EventHandler, LoggingEventHandler
)
from core.patterns.plugin import SFMPlugin, PluginManager, PluginMetadata
from core.patterns.dependency_injection import DIContainer, LifecycleType


class PolicyAnalysisObserver(GraphChangeObserver):
    """Custom observer that analyzes policy impacts when nodes are added."""
    
    def __init__(self):
        self.policy_impacts = []
    
    def on_node_added(self, node):
        if node.__class__.__name__ == "Institution":
            self.policy_impacts.append(f"New institution {node.label} may affect policy landscape")
    
    def on_node_removed(self, node_id):
        self.policy_impacts.append(f"Node {node_id} removed - policy review needed")
    
    def on_node_updated(self, node, previous_state):
        self.policy_impacts.append(f"Node {node.label} updated - analyzing policy implications")
    
    def on_relationship_added(self, relationship):
        self.policy_impacts.append(f"New relationship {relationship.kind} may create policy dependencies")
    
    def on_relationship_removed(self, relationship_id):
        self.policy_impacts.append(f"Relationship {relationship_id} removed - policy chain broken")
    
    def on_relationship_updated(self, relationship, previous_state):
        self.policy_impacts.append(f"Relationship {relationship.kind} updated - reviewing policy effects")
    
    def get_impacts(self):
        return self.policy_impacts.copy()


class GraphAnalysisEventHandler(EventHandler):
    """Event handler that performs analysis when graph changes occur."""
    
    def __init__(self):
        self.analysis_results = []
    
    def handle(self, event: Event):
        if event.event_type == "node_added":
            self.analysis_results.append(f"Analyzing impact of new node: {event.data}")
        elif event.event_type == "centrality_calculated":
            self.analysis_results.append(f"Centrality analysis complete: {event.data}")
    
    def get_results(self):
        return self.analysis_results.copy()


class ExamplePlugin(SFMPlugin):
    """Example plugin that demonstrates the plugin architecture."""
    
    def get_metadata(self):
        return PluginMetadata(
            name="ExamplePlugin",
            version="1.0.0",
            description="Demonstrates plugin architecture",
            author="SFM Framework",
            dependencies=[],
            plugin_type="analyzer"
        )
    
    def initialize(self, framework_context):
        self.framework_context = framework_context
        print("ExamplePlugin initialized")
    
    def cleanup(self):
        print("ExamplePlugin cleaned up")
    
    def register_analyzers(self):
        return {
            "example_analyzer": self.example_analysis
        }
    
    def example_analysis(self, graph):
        """Example analysis function."""
        return {
            "total_nodes": len(graph),
            "analysis_timestamp": datetime.now().isoformat(),
            "plugin_version": "1.0.0"
        }


class AnalysisService:
    """Service for graph analysis (demonstrates dependency injection)."""
    
    def __init__(self, graph: SFMGraph, query_engine: NetworkXSFMQueryEngine):
        self.graph = graph
        self.query_engine = query_engine
    
    def analyze_network_structure(self):
        """Analyze the structure of the network."""
        return {
            "node_count": len(self.graph),
            "relationship_count": len(self.graph.relationships),
            "density": self.query_engine.get_network_density()
        }


def validation_example(name: str, description: str = "") -> bool:
    """Example validation function."""
    return len(name) > 0 and not name.isspace()


@cache_result(ttl=60)
@audit_operation(AuditLevel.INFO)
@validate_inputs(validation_example)
def create_analyzed_actor(name: str, description: str = "") -> Dict[str, Any]:
    """Example function using multiple decorators."""
    # Simulate expensive operation
    time.sleep(0.1)
    
    actor = Actor(
        id=uuid.uuid4(),
        label=name,
        description=description,
        sector="example",
        legal_form="example"
    )
    
    return {
        "actor_id": str(actor.id),
        "name": actor.label,
        "created_at": datetime.now().isoformat()
    }


def demonstrate_observer_pattern():
    """Demonstrate the Observer pattern."""
    print("\n=== OBSERVER PATTERN DEMONSTRATION ===")
    
    # Create graph
    graph = SFMGraph()
    
    # Create observers
    metrics_observer = MetricsObserver()
    caching_observer = CachingObserver()
    policy_observer = PolicyAnalysisObserver()
    
    # Add observers to graph
    graph.add_observer(metrics_observer)
    graph.add_observer(caching_observer)
    graph.add_observer(policy_observer)
    
    # Create and add nodes
    actor = Actor(
        id=uuid.uuid4(),
        label="Department of Agriculture",
        description="Federal agency responsible for agriculture",
        sector="government",
        legal_form="agency"
    )
    
    institution = Institution(
        id=uuid.uuid4(),
        label="Farm Bureau",
        description="Agricultural advocacy organization"
    )
    
    # Add nodes (this will trigger observers)
    graph.add_node(actor)
    graph.add_node(institution)
    
    # Create relationship
    relationship = Relationship(
        id=uuid.uuid4(),
        source_id=actor.id,
        target_id=institution.id,
        kind=RelationshipKind.COLLABORATES_WITH,
        weight=0.8
    )
    
    # Add relationship (this will trigger observers)
    graph.add_relationship(relationship)
    
    # Show observer results
    print(f"Metrics Observer: {metrics_observer.get_metrics()}")
    print(f"Caching Observer invalidated: {len(caching_observer.get_invalidated_caches())} caches")
    print(f"Policy Observer impacts: {len(policy_observer.get_impacts())} impacts detected")
    
    return graph


def demonstrate_command_pattern(graph: SFMGraph):
    """Demonstrate the Command pattern."""
    print("\n=== COMMAND PATTERN DEMONSTRATION ===")
    
    # Create command manager
    command_manager = CommandManager()
    
    # Create a resource
    resource = Resource(
        id=uuid.uuid4(),
        label="Water Rights",
        description="Legal rights to use water resources",
        rtype=ResourceType.REGULATORY,
        unit="acre-feet"
    )
    
    # Create command to add resource
    add_resource_cmd = AddNodeCommand(graph, resource)
    
    # Execute command
    result = command_manager.execute(add_resource_cmd)
    print(f"Executed command: Added {result.label}")
    
    # Show command history
    history = command_manager.get_history()
    print(f"Command history: {len(history)} commands")
    
    # Test undo
    if command_manager.can_undo():
        success = command_manager.undo()
        print(f"Undo successful: {success}")
    
    # Test redo
    if command_manager.can_redo():
        success = command_manager.redo()
        print(f"Redo successful: {success}")
    
    # Create macro command
    actor2 = Actor(
        id=uuid.uuid4(),
        label="EPA",
        description="Environmental Protection Agency",
        sector="government",
        legal_form="agency"
    )
    
    relationship2 = Relationship(
        id=uuid.uuid4(),
        source_id=actor2.id,
        target_id=resource.id,
        kind=RelationshipKind.REGULATES,
        weight=0.9
    )
    
    # Create macro command
    macro_cmd = MacroCommand([
        AddNodeCommand(graph, actor2),
        AddRelationshipCommand(graph, relationship2)
    ], "Add EPA and regulation relationship")
    
    # Execute macro
    results = command_manager.execute(macro_cmd)
    print(f"Executed macro command: {len(results)} operations")
    
    return command_manager


def demonstrate_strategy_pattern(graph: SFMGraph):
    """Demonstrate the Strategy pattern."""
    print("\n=== STRATEGY PATTERN DEMONSTRATION ===")
    
    # Create query engine
    query_engine = NetworkXSFMQueryEngine(graph)
    
    # Test different centrality strategies
    if len(graph) > 0:
        # Get a node to analyze
        node = next(iter(graph))
        
        # Test different centrality algorithms
        strategies = ["betweenness", "closeness", "degree", "eigenvector"]
        
        for strategy in strategies:
            try:
                centrality = query_engine.get_node_centrality(node.id, strategy)
                print(f"{strategy.capitalize()} centrality for {node.label}: {centrality:.4f}")
            except Exception as e:
                print(f"Error calculating {strategy} centrality: {e}")
        
        # Test community detection strategies
        communities = query_engine.identify_communities("louvain")
        print(f"Detected {len(communities)} communities using Louvain algorithm")
    
    # Test strategy manager directly
    strategy_manager = StrategyManager()
    available_strategies = strategy_manager.list_strategies()
    print(f"Available strategies: {available_strategies}")
    
    return query_engine


def demonstrate_decorator_pattern():
    """Demonstrate the Decorator pattern."""
    print("\n=== DECORATOR PATTERN DEMONSTRATION ===")
    
    # Test successful creation
    try:
        result = create_analyzed_actor("Department of Energy", "Federal energy agency")
        print(f"Created actor: {result}")
    except Exception as e:
        print(f"Error creating actor: {e}")
    
    # Test validation failure
    try:
        result = create_analyzed_actor("", "Empty name should fail")
        print(f"Should not reach here: {result}")
    except ValidationError as e:
        print(f"Validation error caught: {e}")
    
    # Test caching (second call should be faster)
    start_time = time.time()
    result = create_analyzed_actor("Department of Energy", "Federal energy agency")
    cached_time = time.time() - start_time
    print(f"Cached call took {cached_time:.4f} seconds")


def demonstrate_event_bus():
    """Demonstrate the Event Bus pattern."""
    print("\n=== EVENT BUS PATTERN DEMONSTRATION ===")
    
    # Create event bus
    event_bus = EventBus()
    
    # Create event handlers
    logging_handler = LoggingEventHandler()
    analysis_handler = GraphAnalysisEventHandler()
    
    # Subscribe handlers
    event_bus.subscribe("node_added", logging_handler)
    event_bus.subscribe("node_added", analysis_handler)
    event_bus.subscribe("centrality_calculated", analysis_handler)
    
    # Publish events
    event_bus.publish(Event("node_added", {"node_id": "123", "type": "Actor"}))
    event_bus.publish(Event("centrality_calculated", {"algorithm": "betweenness", "node_count": 5}))
    
    # Show results
    print(f"Analysis results: {len(analysis_handler.get_results())} events processed")
    
    # Show event history
    history = event_bus.get_event_history()
    print(f"Event history: {len(history)} events")
    
    return event_bus


def demonstrate_plugin_architecture():
    """Demonstrate the Plugin Architecture."""
    print("\n=== PLUGIN ARCHITECTURE DEMONSTRATION ===")
    
    # Create plugin manager
    plugin_manager = PluginManager()
    
    # Create and load plugin
    plugin = ExamplePlugin()
    
    # Manually register plugin (in real usage, this would be done via discovery)
    plugin_manager._plugins["ExamplePlugin"] = type('PluginInfo', (), {
        'plugin_instance': plugin,
        'metadata': plugin.get_metadata(),
        'status': type('Status', (), {'LOADED': 'loaded'})().LOADED
    })()
    
    # Initialize plugin
    plugin.initialize({"framework_version": "1.0.0"})
    
    # Activate plugin
    plugin_manager.activate_plugin("ExamplePlugin")
    
    # Get plugin registry
    registry = plugin_manager.get_plugin_registry()
    analyzer = registry.get_analyzer("example_analyzer")
    
    if analyzer:
        # Test plugin analyzer
        graph = SFMGraph()
        result = analyzer(graph)
        print(f"Plugin analysis result: {result}")
    
    # Show plugin statistics
    stats = plugin_manager.get_statistics()
    print(f"Plugin manager statistics: {stats}")
    
    return plugin_manager


def demonstrate_dependency_injection():
    """Demonstrate the Dependency Injection pattern."""
    print("\n=== DEPENDENCY INJECTION DEMONSTRATION ===")
    
    # Create DI container
    container = DIContainer()
    
    # Register services
    container.register_singleton(SFMGraph, SFMGraph())
    container.register_transient(NetworkXSFMQueryEngine)
    container.register_transient(AnalysisService)
    
    # Get services
    graph = container.get(SFMGraph)
    analysis_service = container.get(AnalysisService)
    
    # Use service
    analysis = analysis_service.analyze_network_structure()
    print(f"Network analysis: {analysis}")
    
    # Show container statistics
    stats = container.get_metrics()
    print(f"DI container statistics: {stats}")
    
    return container


def main():
    """Main demonstration function."""
    print("SFM Framework Design Patterns Demonstration")
    print("=" * 50)
    
    # Demonstrate each pattern
    graph = demonstrate_observer_pattern()
    command_manager = demonstrate_command_pattern(graph)
    query_engine = demonstrate_strategy_pattern(graph)
    demonstrate_decorator_pattern()
    event_bus = demonstrate_event_bus()
    plugin_manager = demonstrate_plugin_architecture()
    container = demonstrate_dependency_injection()
    
    print("\n=== INTEGRATION DEMONSTRATION ===")
    print("All patterns working together:")
    print(f"- Graph has {len(graph)} nodes and {len(graph.relationships)} relationships")
    print(f"- Command manager has {len(command_manager.get_history())} commands in history")
    print(f"- Query engine supports {len(query_engine.strategy_manager.list_strategies())} strategy categories")
    print(f"- Event bus processed {len(event_bus.get_event_history())} events")
    print(f"- Plugin manager has {plugin_manager.get_statistics()['total_plugins']} plugins")
    print(f"- DI container has {container.get_metrics()['registered_services']} registered services")
    
    print("\n=== BENEFITS ACHIEVED ===")
    print("✓ Maintainability: Clean separation of concerns")
    print("✓ Extensibility: Plugin system for custom functionality")
    print("✓ Testability: Dependency injection for unit testing")
    print("✓ Robustness: Command pattern for operation recovery")
    print("✓ Performance: Decorator pattern for caching and optimization")
    print("✓ Modularity: Event bus for loose coupling")
    print("✓ Flexibility: Strategy pattern for algorithm switching")
    
    print("\nDesign patterns demonstration completed successfully!")


if __name__ == "__main__":
    main()
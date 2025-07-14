# Design Patterns in SFM Framework

This document provides comprehensive guidance on using the design patterns implemented in the SFM (Social Fabric Matrix) framework. These patterns enhance maintainability, extensibility, and robustness of the system.

## Overview

The SFM framework now includes implementations of the following design patterns:

1. **Observer Pattern** - For graph change notifications
2. **Command Pattern** - For undo/redo operations 
3. **Strategy Pattern** - For pluggable algorithms
4. **Decorator Pattern** - For cross-cutting concerns
5. **Event Bus Pattern** - For loose coupling between components
6. **Plugin Architecture** - For framework extensions
7. **Dependency Injection** - For improved testability

## 1. Observer Pattern

The Observer pattern allows components to be notified when the graph changes.

### Basic Usage

```python
from core.graph import SFMGraph
from core.patterns.observer import MetricsObserver, CachingObserver

# Create graph
graph = SFMGraph()

# Create observers
metrics_observer = MetricsObserver()
cache_observer = CachingObserver()

# Add observers
graph.add_observer(metrics_observer)
graph.add_observer(cache_observer)

# Any changes to the graph will now notify observers
actor = Actor(id=uuid.uuid4(), label="Test Actor")
graph.add_node(actor)  # Triggers notifications

# Check metrics
print(metrics_observer.get_metrics())
```

### Creating Custom Observers

```python
from core.patterns.observer import GraphChangeObserver

class PolicyAnalysisObserver(GraphChangeObserver):
    def __init__(self):
        self.policy_impacts = []
    
    def on_node_added(self, node):
        if isinstance(node, Policy):
            self.policy_impacts.append(f"New policy: {node.label}")
    
    def on_relationship_added(self, relationship):
        if relationship.kind == RelationshipKind.INFLUENCES:
            self.policy_impacts.append("New influence relationship detected")
    
    # Implement other abstract methods...
```

### Available Observers

- `MetricsObserver` - Tracks graph change statistics
- `CachingObserver` - Invalidates caches when graph changes
- Custom observers can be created by implementing `GraphChangeObserver`

## 2. Command Pattern

The Command pattern enables undo/redo functionality for graph operations.

### Basic Usage

```python
from core.patterns.command import CommandManager, AddNodeCommand

# Create command manager
command_manager = CommandManager()

# Create command
actor = Actor(id=uuid.uuid4(), label="Department of Agriculture")
add_command = AddNodeCommand(graph, actor)

# Execute command
result = command_manager.execute(add_command)

# Undo operation
if command_manager.can_undo():
    command_manager.undo()

# Redo operation
if command_manager.can_redo():
    command_manager.redo()
```

### Complex Operations with Macro Commands

```python
from core.patterns.command import MacroCommand, AddRelationshipCommand

# Create multiple commands
commands = [
    AddNodeCommand(graph, actor1),
    AddNodeCommand(graph, actor2),
    AddRelationshipCommand(graph, relationship)
]

# Execute as a single unit
macro_command = MacroCommand(commands, "Add actors and relationship")
command_manager.execute(macro_command)

# Undo all operations at once
command_manager.undo()
```

### Available Commands

- `AddNodeCommand` - Add a node to the graph
- `RemoveNodeCommand` - Remove a node from the graph
- `AddRelationshipCommand` - Add a relationship to the graph
- `RemoveRelationshipCommand` - Remove a relationship from the graph
- `MacroCommand` - Execute multiple commands as a single unit

## 3. Strategy Pattern

The Strategy pattern allows pluggable algorithms for graph analysis.

### Basic Usage

```python
from core.sfm_query import NetworkXSFMQueryEngine

# Create query engine (now uses strategies internally)
query_engine = NetworkXSFMQueryEngine(graph)

# Use different centrality algorithms
betweenness = query_engine.get_node_centrality(node_id, "betweenness")
closeness = query_engine.get_node_centrality(node_id, "closeness")
eigenvector = query_engine.get_node_centrality(node_id, "eigenvector")
```

### Using Strategy Manager Directly

```python
from core.patterns.strategy import StrategyManager, CentralityAnalyzer

# Create strategy manager
strategy_manager = StrategyManager()

# List available strategies
print(strategy_manager.list_strategies())

# Use centrality analyzer
analyzer = CentralityAnalyzer(strategy_manager)
centrality = analyzer.calculate_centrality(nx_graph, node_id, "betweenness")
```

### Creating Custom Strategies

```python
from core.patterns.strategy import CentralityStrategy

class CustomCentralityStrategy(CentralityStrategy):
    def get_name(self):
        return "custom"
    
    def get_description(self):
        return "Custom centrality algorithm"
    
    def calculate(self, graph, node_id):
        # Implement custom algorithm
        return custom_centrality_value
    
    def calculate_all(self, graph):
        # Calculate for all nodes
        return {node_id: self.calculate(graph, node_id) for node_id in graph.nodes()}

# Register custom strategy
strategy_manager.register_strategy("centrality", CustomCentralityStrategy())
```

### Available Strategy Categories

- **Centrality**: `betweenness`, `closeness`, `degree`, `eigenvector`
- **Community Detection**: `louvain`, `label_propagation`, `greedy_modularity`
- **Path Finding**: `shortest_path`, `all_shortest_paths`

## 4. Decorator Pattern

The Decorator pattern provides cross-cutting concerns like validation, caching, and auditing.

### Basic Usage

```python
from core.patterns.decorator import cache_result, audit_operation, validate_inputs
from core.patterns.decorator import AuditLevel, ValidationError

@cache_result(ttl=3600)
@audit_operation(AuditLevel.INFO)
@validate_inputs(lambda name: len(name) > 0)
def create_actor(name: str):
    # Function implementation
    return Actor(id=uuid.uuid4(), label=name)

# Function calls are now cached, audited, and validated
actor = create_actor("Department of Energy")
```

### Available Decorators

- `@cache_result(ttl=3600)` - Cache function results
- `@audit_operation(level=AuditLevel.INFO)` - Audit function calls
- `@validate_inputs(validator_func)` - Validate function inputs
- `@time_execution()` - Time function execution
- `@retry_on_failure(max_retries=3)` - Retry failed operations

### Creating Custom Decorators

```python
from core.patterns.decorator import Decorator

class LoggingDecorator(Decorator):
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"Calling {func.__name__}")
            result = func(*args, **kwargs)
            print(f"Finished {func.__name__}")
            return result
        return wrapper
```

## 5. Event Bus Pattern

The Event Bus enables loose coupling between components through event-driven architecture.

### Basic Usage

```python
from core.patterns.event_bus import EventBus, Event, EventHandler

# Create event bus
event_bus = EventBus()

# Create event handler
class GraphAnalysisHandler(EventHandler):
    def handle(self, event):
        if event.event_type == "node_added":
            print(f"Analyzing new node: {event.data}")

# Subscribe handler
handler = GraphAnalysisHandler()
event_bus.subscribe("node_added", handler)

# Publish event
event = Event("node_added", {"node_id": "123", "type": "Actor"})
event_bus.publish(event)
```

### Asynchronous Event Handling

```python
from core.patterns.event_bus import AsyncEventHandler

class AsyncAnalysisHandler(AsyncEventHandler):
    async def handle_async(self, event):
        # Perform async analysis
        await perform_complex_analysis(event.data)

# Subscribe async handler
event_bus.subscribe("complex_analysis", AsyncAnalysisHandler())

# Start async processing
await event_bus.start_async_processing()
```

### Event Filtering and Middleware

```python
# Add event filter
event_bus.add_filter(lambda event: event.priority.value > 2)

# Add middleware
def enrich_event(event):
    event.metadata["processed_at"] = datetime.now()
    return event

event_bus.add_middleware(enrich_event)
```

## 6. Plugin Architecture

The Plugin Architecture allows extending the framework with custom functionality.

### Creating a Plugin

```python
from core.patterns.plugin import SFMPlugin, PluginMetadata

class MyAnalysisPlugin(SFMPlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="MyAnalysisPlugin",
            version="1.0.0",
            description="Custom analysis plugin",
            author="Your Name",
            dependencies=[]
        )
    
    def initialize(self, framework_context):
        self.context = framework_context
        print("Plugin initialized")
    
    def cleanup(self):
        print("Plugin cleaned up")
    
    def register_analyzers(self):
        return {
            "my_analysis": self.perform_analysis
        }
    
    def perform_analysis(self, graph):
        # Custom analysis logic
        return {"result": "analysis_data"}
```

### Using Plugin Manager

```python
from core.patterns.plugin import PluginManager

# Create plugin manager
plugin_manager = PluginManager()

# Load plugin
plugin_manager.load_plugin("my_plugin", Path("path/to/plugin.py"))

# Activate plugin
plugin_manager.activate_plugin("my_plugin")

# Use plugin functionality
registry = plugin_manager.get_plugin_registry()
analyzer = registry.get_analyzer("my_analysis")
result = analyzer(graph)
```

### Plugin Capabilities

Plugins can register:
- **Entities** - Custom node types
- **Relationships** - Custom relationship kinds
- **Analyzers** - Custom analysis functions
- **Validators** - Custom validation functions
- **Event Handlers** - Custom event handlers
- **API Endpoints** - Custom API endpoints

## 7. Dependency Injection

The Dependency Injection pattern improves testability and flexibility.

### Basic Usage

```python
from core.patterns.dependency_injection import DIContainer, LifecycleType

# Create container
container = DIContainer()

# Register services
container.register_singleton(SFMGraph, SFMGraph())
container.register_transient(NetworkXSFMQueryEngine)

# Get services (dependencies are automatically resolved)
graph = container.get(SFMGraph)
query_engine = container.get(NetworkXSFMQueryEngine)
```

### Service Lifetimes

```python
# Singleton - single instance
container.register_singleton(ConfigService, ConfigService())

# Transient - new instance every time
container.register_transient(AnalysisService)

# Scoped - single instance per scope
container.register_scoped(DatabaseConnection)

# Using scopes
with container.scope() as scope:
    service1 = scope.get_service(DatabaseConnection)
    service2 = scope.get_service(DatabaseConnection)
    # service1 and service2 are the same instance
```

### Factory Registration

```python
# Register factory function
def create_analyzer(graph: SFMGraph):
    return CustomAnalyzer(graph)

container.register_factory(CustomAnalyzer, create_analyzer)
```

### Service Interception

```python
# Add interceptor
def logging_interceptor(service_type, instance):
    print(f"Created {service_type.__name__}")
    return instance

container.add_interceptor(logging_interceptor)
```

## Integration Examples

### Complete Analysis Pipeline

```python
from core.sfm_service import SFMService
from core.patterns.observer import MetricsObserver
from core.patterns.command import CommandManager
from core.patterns.event_bus import EventBus, Event

# Create service
service = SFMService()

# Add observer
observer = MetricsObserver()
service.get_graph().add_observer(observer)

# Create command manager
command_manager = CommandManager()

# Create event bus
event_bus = EventBus()

# Create actor with command pattern
actor = Actor(id=uuid.uuid4(), label="EPA")
add_command = AddNodeCommand(service.get_graph(), actor)
command_manager.execute(add_command)

# Publish event
event_bus.publish(Event("actor_created", {"actor_id": str(actor.id)}))

# Check observer metrics
print(observer.get_metrics())
```

### Plugin-Based Analysis

```python
# Load analysis plugin
plugin_manager.load_plugin("advanced_analysis")
plugin_manager.activate_plugin("advanced_analysis")

# Get plugin analyzer
registry = plugin_manager.get_plugin_registry()
analyzer = registry.get_analyzer("network_vulnerability")

# Perform analysis
result = analyzer(service.get_graph())
```

## Best Practices

### Observer Pattern
- Keep observers lightweight and fast
- Handle exceptions in observers to prevent cascading failures
- Use observers for monitoring and logging, not business logic

### Command Pattern
- Make commands idempotent when possible
- Include validation in command execution
- Use macro commands for complex operations

### Strategy Pattern
- Design strategies to be stateless
- Provide clear documentation for strategy parameters
- Test strategies with various graph sizes and structures

### Decorator Pattern
- Order decorators carefully (validation before caching)
- Keep decorators focused on single concerns
- Use decorator chains for complex cross-cutting functionality

### Event Bus
- Use meaningful event names and consistent data structures
- Implement proper error handling in event handlers
- Consider async processing for time-consuming operations

### Plugin Architecture
- Define clear plugin interfaces
- Implement proper dependency management
- Provide plugin health monitoring and error recovery

### Dependency Injection
- Register services at application startup
- Use appropriate lifetimes for different service types
- Validate container configuration at startup

## Performance Considerations

- **Caching**: Use decorator caching for expensive operations
- **Lazy Loading**: Load plugins and strategies only when needed
- **Memory Management**: Monitor observer and event handler memory usage
- **Async Processing**: Use async event handling for non-blocking operations

## Testing

All patterns include comprehensive unit tests. Run tests with:

```bash
python -m pytest tests/test_design_patterns.py -v
```

## Migration Guide

### From Direct Graph Operations

**Before:**
```python
graph.add_node(node)
```

**After:**
```python
# With observer pattern
graph.add_observer(observer)
graph.add_node(node)  # Observers are automatically notified

# With command pattern
command = AddNodeCommand(graph, node)
command_manager.execute(command)
```

### From Hard-coded Algorithms

**Before:**
```python
centrality = nx.betweenness_centrality(graph)
```

**After:**
```python
# With strategy pattern
query_engine = NetworkXSFMQueryEngine(graph)
centrality = query_engine.get_node_centrality(node_id, "betweenness")
```

## Conclusion

These design patterns significantly enhance the SFM framework's maintainability, extensibility, and robustness. They provide a solid foundation for building complex social fabric analysis applications with clean, testable, and flexible code.

For more examples and detailed API documentation, see the `examples/` directory and the comprehensive test suite in `tests/test_design_patterns.py`.
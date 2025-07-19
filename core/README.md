# Core Module Documentation

This directory provides a unified interface for all Social Fabric Matrix (SFM) components, maintaining backward compatibility while the underlying implementation has been reorganized into specialized modules.

## Module Purpose

The core module serves as a **backward compatibility layer**, allowing existing code to continue working while providing access to the reorganized modular structure introduced in recent versions.

## Current Structure

### **Unified Import Interface**

#### `sfm_models.py` - **Main Import Module** 
This is the primary entry point that imports all SFM classes from their new locations:

```python
# All these imports work seamlessly:
from core.sfm_models import Actor, Institution, Resource, SFMGraph
from core.sfm_models import Relationship, TimeSlice, Scenario
```

The module imports from the new modular structure:
- **`models/`** - Data model implementations
- **`graph/`** - Graph operations and analysis  
- **`api/`** - Service layer and high-level API

## New Modular Organization

The actual implementation has been reorganized for better maintainability:

### **Implementation Modules**

#### `models/` - **Data Model Implementation Directory**
- `base_nodes.py` - Base Node class and infrastructure
- `core_nodes.py` - Primary SFM entities (Actor, Institution, etc.)
- `specialized_nodes.py` - Specialized components (TechnologySystem, etc.)
- `behavioral_nodes.py` - Behavioral and cognitive components
- `meta_entities.py` - Dimensional entities (TimeSlice, SpatialUnit, Scenario)
- `relationships.py` - Graph relationships and connections
- `sfm_enums.py` - Comprehensive enumeration definitions
- `metadata_models.py` - Support and metadata classes
- `exceptions.py` - Custom exception classes

#### `graph/` - **Graph Operations and Analysis Directory**
- `graph.py` - SFMGraph and NetworkMetrics classes
- `sfm_query.py` - Query engine abstractions and implementations
- `sfm_persistence.py` - Graph persistence and serialization utilities

#### `api/` - **Service Layer Directory**
- `sfm_service.py` - High-level service facade for simplified usage

#### `data/` - **Data Access and Storage Layer Directory**  
- `repositories.py` - Repository pattern implementation (CRUD operations)

## Core Data Model

The SFM framework models socio-economic systems as networks of interconnected entities. Here are the main components:

### Node Types (Entities)

```
Node (Base Class)
├── Actor           # Decision-making entities (agencies, firms, individuals)
├── Institution     # Rules and organizations
│   └── Policy      # Specific interventions
├── Resource        # Stocks and assets
├── Process         # Transformation activities
├── Flow            # Quantified transfers
├── Indicator       # Performance measures
└── Other specialized types...
```

### Dimensional Entities

```
TimeSlice    # Temporal context (e.g., "Q1-2025")
SpatialUnit  # Geographic boundaries (e.g., "US-WA-SEATTLE")
Scenario     # Policy alternatives (e.g., "Carbon Tax 2026")
```

### Relationships

Relationships connect entities with typed, weighted connections:

```
Relationship
├── source_id: UUID
├── target_id: UUID
├── kind: RelationshipKind
├── weight: float
└── dimensional context (time, space, scenario)
```

## Example SFM Matrix Structure

Here's a simplified representation of how entities relate in a grain market analysis:

```
           USDA  Farmers  Traders  Grain  Subsidy
USDA        -      0.8      -       -      0.9
Farmers     -       -      0.6     0.7     -
Traders     -       -       -      0.5     -
Grain       -       -       -       -      -
Subsidy    0.5     0.8      -       -      -
```

Where values represent relationship weights (e.g., influence strength, flow volume).

## Usage Patterns

The core module supports multiple import patterns for different use cases:

### **Recommended: Unified Import (Backward Compatible)**
```python
from core.sfm_models import *

# All classes are available through the unified interface
actor = Actor(label="Test Actor", sector="Government")
graph = SFMGraph(name="Example")
graph.add_node(actor)
```

### **Selective Imports from Core**
```python
from core.sfm_models import Actor, Institution, SFMGraph, TimeSlice, Indicator
```

### **Direct Module Imports (Advanced)**
For users who want to import directly from the implementation modules:

```python
# Import from models directory
from models.core_nodes import Actor, Institution
from models.behavioral_nodes import ValueSystem  
from models.sfm_enums import RelationshipKind, ResourceType

# Import from graph directory
from graph.graph import SFMGraph
from graph.sfm_query import SFMQueryFactory

# Import from api directory  
from api.sfm_service import SFMService
```

## Basic Usage Example

```python
from core.sfm_models import SFMGraph, Actor, Resource, Relationship
from models.sfm_enums import RelationshipKind, ResourceType

# Create entities
government = Actor(label="Government", sector="Public")
grain = Resource(label="Wheat", rtype=ResourceType.BIOLOGICAL)

# Create relationship
regulation = Relationship(
    source_id=government.id,
    target_id=grain.id,
    kind=RelationshipKind.REGULATES,
    weight=0.7
)

# Build graph
graph = SFMGraph(name="Simple Market Model")
graph.add_node(government)
graph.add_node(grain)
graph.add_relationship(regulation)
```

## Benefits of the Modular Structure

1. **Backward Compatibility** - Existing code using `from core.sfm_models import *` continues to work
2. **Better Organization** - Related classes are grouped together in focused modules under `models/`, `graph/`, `api/`
3. **Reduced Complexity** - Smaller, focused modules are easier to understand and maintain
4. **Improved Maintainability** - Changes can be made to specific areas without affecting others
5. **Clear Separation of Concerns** - Each directory has a specific responsibility:
   - `models/` - Data structures and business logic
   - `graph/` - Graph operations and network analysis
   - `api/` - Service layer and high-level interface
   - `db/` - Data persistence and repository patterns
6. **Type Safety** - Improved type hints and reduced circular dependencies
7. **Selective Imports** - Import only what you need for better performance

## Migration Notes

**No migration required!** The core module maintains full backward compatibility. However, users can optionally benefit from:

- **Better Performance**: Direct imports from specific modules reduce import overhead
- **Enhanced IDE Support**: More specific imports improve code completion and error detection  
- **Clearer Dependencies**: Understanding which specific modules your code depends on

## Quick Start with SFM Service

For the easiest experience, use the high-level service interface:

```python
from api.sfm_service import SFMService

# Create service instance
service = SFMService()

# Create entities using high-level methods
usda = service.create_actor("USDA", "US Department of Agriculture", sector="government")
farm_bill = service.create_policy("Farm Bill 2023", "Agricultural support legislation", authority="US Congress")

# Create relationships
service.connect(usda.id, farm_bill.id, "IMPLEMENTS")

# Analyze the network
stats = service.get_statistics()
print(f"Graph has {stats['total_nodes']} nodes")
```

## Entity Relationship Diagram

```
    Actor ────────────────┐
      │                   │
      │ governs           │ affects
      ▼                   ▼
  Institution ──────► Resource
      │                   ▲
      │ implements        │ uses
      ▼                   │
    Policy ──────────► Process
      │                   │
      │ creates           │ produces
      ▼                   ▼
    Flow ◄─────────────► Indicator
```

## Relationship Types (Key Examples)

From `sfm_enums.py`, relationships are categorized by function:

- **Governance**: GOVERNS, REGULATES, AUTHORIZES
- **Economic**: FUNDS, PAYS, TRADES, PRODUCES
- **Information**: INFORMS, ANALYZES, COMMUNICATES
- **Process**: TRANSFORMS, EXTRACTS, OPERATES

## Query Engine Capabilities

The `sfm_query.py` module provides analysis functions:

### Network Analysis
- Node centrality calculations
- Shortest path finding
- Community detection

### Policy Analysis
- Impact radius assessment
- Target identification
- Scenario comparison

### Flow Analysis
- Resource flow tracing
- Bottleneck identification
- Efficiency calculations

## Simple Matrix Creation Process

1. **Define Entities**: Create actors, institutions, resources, etc.
2. **Establish Relationships**: Connect entities with typed relationships
3. **Build Graph**: Use `SFMGraph` to organize the network
4. **Generate Matrix**: Filter relationships by type and aggregate weights
5. **Analyze**: Use query engine for network analysis

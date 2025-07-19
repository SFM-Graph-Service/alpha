# SFM-Graph-Service: `db` Module

This module implements an abstract data access layer for Social Fabric Matrix (SFM) graph data, supporting flexible storage backends (default: in-memory with NetworkX).

---

## Table of Contents
- [Overview](#overview)
- [Core Repository Interfaces](#core-repository-interfaces)
  - [SFMRepository (abstract)](#sfmrepository-abstract)
  - [NetworkXSFMRepository](#networkxsfmrepository)
- [Type-Safe Repositories](#type-safe-repositories)
  - [TypedSFMRepository](#typedsfmrepository)
  - [ActorRepository](#actorrepository)
  - [InstitutionRepository](#institutionrepository)
  - [PolicyRepository](#policyrepository)
  - [ResourceRepository](#resourcerepository)
  - [RelationshipRepository](#relationshiprepository)
- [Repository Factory](#repository-factory)
- [Usage Example](#usage-example)

---

## Overview

The `db` module provides an extensible and type-safe way to interact with SFM graph data, including nodes (such as Actor, Institution, Resource, Policy) and relationships. It supports CRUD operations, querying, and complete graph loading/saving.

---

## Core Repository Interfaces

### `SFMRepository` (abstract)

*Defines the abstract interface for CRUD operations on nodes and relationships, plus graph-wide operations.*

**Key Methods:**
- `create_node(node: Node) -> Node`
- `read_node(node_id: uuid.UUID) -> Optional[Node]`
- `update_node(node: Node) -> Node`
- `delete_node(node_id: uuid.UUID) -> bool`
- `list_nodes(node_type: Optional[Type[Node]]) -> List[Node]`
- `create_relationship(rel: Relationship) -> Relationship`
- `read_relationship(rel_id: uuid.UUID) -> Optional[Relationship]`
- `update_relationship(rel: Relationship) -> Relationship`
- `delete_relationship(rel_id: uuid.UUID) -> bool`
- `list_relationships(kind: Optional[RelationshipKind]) -> List[Relationship]`
- `find_relationships(source_id, target_id, kind) -> List[Relationship]`
- `load_graph() -> SFMGraph`
- `save_graph(graph: SFMGraph) -> None`
- `clear() -> None`

---

### `NetworkXSFMRepository`

*Concrete implementation of `SFMRepository` using an in-memory [NetworkX](https://networkx.org/) MultiDiGraph.*

- Stores node objects and relationships (edges) with full data.
- Supports all CRUD and query operations as defined in the abstract interface.
- Can load/save the entire SFM graph to/from memory.

---

## Type-Safe Repositories

### `TypedSFMRepository[T]`

*A generic, type-safe repository wrapper for specific node types.*

**Key Features:**
- Ensures only the specified node type can be stored and retrieved.
- Supports attribute-based filtering with the `query` method.

#### Methods:
- `create(node: T) -> T`
- `read(node_id: uuid.UUID) -> Optional[T]`
- `update(node: T) -> T`
- `delete(node_id: uuid.UUID) -> bool`
- `list_all() -> List[T]`
- `query(filters: Dict[str, Any]) -> List[T]`

---

### `ActorRepository`

*Specialized for `Actor` entities. Inherits from `TypedSFMRepository[Actor]`.*

- `find_by_sector(sector: str) -> List[Actor]`
- `find_by_legal_form(legal_form: str) -> List[Actor]`

---

### `InstitutionRepository`

*Specialized for `Institution` entities. Inherits from `TypedSFMRepository[Institution]`.*

---

### `PolicyRepository`

*Specialized for `Policy` entities. Inherits from `TypedSFMRepository[Policy]`.*

- `find_by_authority(authority: str) -> List[Policy]`
- `find_by_target_sector(sector: str) -> List[Policy]`

---

### `ResourceRepository`

*Specialized for `Resource` entities. Inherits from `TypedSFMRepository[Resource]`.*

- `find_by_type(rtype: ResourceType) -> List[Resource]`

---

### `RelationshipRepository`

*Type-safe repository for `Relationship` entities.*

**Key Methods:**
- `create(relationship: Relationship) -> Relationship`
- `read(rel_id: uuid.UUID) -> Optional[Relationship]`
- `update(relationship: Relationship) -> Relationship`
- `delete(rel_id: uuid.UUID) -> bool`
- `list_all() -> List[Relationship]`
- `find_by_kind(kind: RelationshipKind) -> List[Relationship]`
- `find_by_source(source_id: uuid.UUID) -> List[Relationship]`
- `find_by_target(target_id: uuid.UUID) -> List[Relationship]`
- `find_by_nodes(source_id: uuid.UUID, target_id: uuid.UUID) -> List[Relationship]`

---

## Repository Factory

### `SFMRepositoryFactory`

*Factory class for creating repositories with different storage backends.*

**Key Methods:**
- `create_repository(storage_type: str = "networkx") -> SFMRepository`
- `create_actor_repository(storage_type: str = "networkx") -> ActorRepository`
- `create_institution_repository(storage_type: str = "networkx") -> InstitutionRepository`
- `create_policy_repository(storage_type: str = "networkx") -> PolicyRepository`
- `create_resource_repository(storage_type: str = "networkx") -> ResourceRepository`
- `create_relationship_repository(storage_type: str = "networkx") -> RelationshipRepository`

---

## Usage Example

```python
from db.sfm_dao import SFMRepositoryFactory

# Create an in-memory repository for actors
actor_repo = SFMRepositoryFactory.create_actor_repository()

# Create a new actor (requires an Actor instance)
# actor = Actor(...)
# actor_repo.create(actor)

# Query actors by sector
# actors_in_sector = actor_repo.find_by_sector("public")
```

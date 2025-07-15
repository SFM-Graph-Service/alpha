"""
Plugin Architecture Implementation for SFM Framework

This module implements a plugin system that allows for easy extension of the
SFM framework with custom entities, relationships, and analysis capabilities.
"""

import uuid
import importlib
import importlib.util
import inspect
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

from core.base_nodes import Node
from core.relationships import Relationship
from core.sfm_enums import RelationshipKind


class PluginStatus(Enum):
    """Status of a plugin."""
    LOADED = "loaded"
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """Metadata about a plugin."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = field(default_factory=list)
    min_framework_version: str = "1.0.0"
    max_framework_version: Optional[str] = None
    plugin_type: str = "extension"
    tags: List[str] = field(default_factory=list)
    website: Optional[str] = None
    license: Optional[str] = None


@dataclass
class PluginInfo:
    """Information about a loaded plugin."""
    metadata: PluginMetadata
    plugin_instance: 'SFMPlugin'
    status: PluginStatus
    loaded_at: datetime
    activated_at: Optional[datetime] = None
    deactivated_at: Optional[datetime] = None
    error_message: Optional[str] = None
    load_time_ms: float = 0.0


class SFMPlugin(ABC):
    """Abstract base class for SFM plugins."""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, framework_context: Dict[str, Any]) -> None:
        """Initialize the plugin with framework context."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

    def register_entities(self) -> List[Type[Node]]:
        """Register custom entity types."""
        return []

    def register_relationships(self) -> List[RelationshipKind]:
        """Register custom relationship kinds."""
        return []

    def register_analyzers(self) -> Dict[str, Callable]:
        """Register custom analysis functions."""
        return {}

    def register_validators(self) -> Dict[str, Callable]:
        """Register custom validation functions."""
        return {}

    def register_event_handlers(self) -> Dict[str, Callable]:
        """Register custom event handlers."""
        return {}

    def get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for this plugin."""
        return {}

    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin with settings."""
        pass

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the plugin."""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin-specific metrics."""
        return {}


class PluginRegistry:
    """Registry for managing entity types and relationships from plugins."""

    def __init__(self):
        self._entity_types: Dict[str, Type[Node]] = {}
        self._relationship_kinds: Dict[str, RelationshipKind] = {}
        self._analyzers: Dict[str, Callable] = {}
        self._validators: Dict[str, Callable] = {}
        self._event_handlers: Dict[str, Callable] = {}
        # Maps resource name to plugin name
        self._plugin_owners: Dict[str, str] = {}

    def register_entity_type(
            self,
            entity_type: Type[Node],
            plugin_name: str) -> None:
        """Register a custom entity type."""
        type_name = entity_type.__name__

        if type_name in self._entity_types:
            raise ValueError(f"Entity type {type_name} already registered")

        self._entity_types[type_name] = entity_type
        self._plugin_owners[f"entity:{type_name}"] = plugin_name

    def register_relationship_kind(
            self,
            relationship_kind: RelationshipKind,
            plugin_name: str) -> None:
        """Register a custom relationship kind."""
        kind_name = relationship_kind.name

        if kind_name in self._relationship_kinds:
            raise ValueError(
                f"Relationship kind {kind_name} already registered")

        self._relationship_kinds[kind_name] = relationship_kind
        self._plugin_owners[f"relationship:{kind_name}"] = plugin_name

    def register_analyzer(
            self,
            name: str,
            analyzer: Callable,
            plugin_name: str) -> None:
        """Register a custom analyzer function."""
        if name in self._analyzers:
            raise ValueError(f"Analyzer {name} already registered")

        self._analyzers[name] = analyzer
        self._plugin_owners[f"analyzer:{name}"] = plugin_name

    def register_validator(
            self,
            name: str,
            validator: Callable,
            plugin_name: str) -> None:
        """Register a custom validator function."""
        if name in self._validators:
            raise ValueError(f"Validator {name} already registered")

        self._validators[name] = validator
        self._plugin_owners[f"validator:{name}"] = plugin_name

    def register_event_handler(
            self,
            event_type: str,
            handler: Callable,
            plugin_name: str) -> None:
        """Register a custom event handler."""
        if event_type in self._event_handlers:
            raise ValueError(
                f"Event handler for {event_type} already registered")

        self._event_handlers[event_type] = handler
        self._plugin_owners[f"event:{event_type}"] = plugin_name

    def get_entity_type(self, type_name: str) -> Optional[Type[Node]]:
        """Get an entity type by name."""
        return self._entity_types.get(type_name)

    def get_relationship_kind(
            self,
            kind_name: str) -> Optional[RelationshipKind]:
        """Get a relationship kind by name."""
        return self._relationship_kinds.get(kind_name)

    def get_analyzer(self, name: str) -> Optional[Callable]:
        """Get an analyzer by name."""
        return self._analyzers.get(name)

    def get_validator(self, name: str) -> Optional[Callable]:
        """Get a validator by name."""
        return self._validators.get(name)

    def get_event_handler(self, event_type: str) -> Optional[Callable]:
        """Get an event handler by event type."""
        return self._event_handlers.get(event_type)

    def unregister_plugin_resources(self, plugin_name: str) -> None:
        """Unregister all resources from a specific plugin."""
        # Find all resources owned by this plugin
        resources_to_remove = [
            resource for resource, owner in self._plugin_owners.items()
            if owner == plugin_name
        ]

        for resource in resources_to_remove:
            resource_type, resource_name = resource.split(":", 1)

            if resource_type == "entity":
                self._entity_types.pop(resource_name, None)
            elif resource_type == "relationship":
                self._relationship_kinds.pop(resource_name, None)
            elif resource_type == "analyzer":
                self._analyzers.pop(resource_name, None)
            elif resource_type == "validator":
                self._validators.pop(resource_name, None)
            elif resource_type == "event":
                self._event_handlers.pop(resource_name, None)

            del self._plugin_owners[resource]

    def get_registered_resources(self) -> Dict[str, List[str]]:
        """Get all registered resources by type."""
        return {
            "entity_types": list(self._entity_types.keys()),
            "relationship_kinds": list(self._relationship_kinds.keys()),
            "analyzers": list(self._analyzers.keys()),
            "validators": list(self._validators.keys()),
            "event_handlers": list(self._event_handlers.keys())
        }

    def get_plugin_resources(self, plugin_name: str) -> Dict[str, List[str]]:
        """Get all resources registered by a specific plugin."""
        plugin_resources: Dict[str, List[str]] = {
            "entity_types": [],
            "relationship_kinds": [],
            "analyzers": [],
            "validators": [],
            "event_handlers": []
        }

        for resource, owner in self._plugin_owners.items():
            if owner == plugin_name:
                resource_type, resource_name = resource.split(":", 1)
                if resource_type == "entity":
                    plugin_resources["entity_types"].append(resource_name)
                elif resource_type == "relationship":
                    plugin_resources["relationship_kinds"].append(
                        resource_name)
                elif resource_type == "analyzer":
                    plugin_resources["analyzers"].append(resource_name)
                elif resource_type == "validator":
                    plugin_resources["validators"].append(resource_name)
                elif resource_type == "event":
                    plugin_resources["event_handlers"].append(resource_name)

        return plugin_resources


class PluginManager:
    """
    Manager for loading, activating, and managing plugins.

    This class handles the plugin lifecycle and provides a unified interface
    for plugin management.
    """

    def __init__(self):
        self._plugins: Dict[str, PluginInfo] = {}
        self._plugin_registry = PluginRegistry()
        self._plugin_directories: List[Path] = []
        self._framework_context: Dict[str, Any] = {}
        self._dependency_graph: Dict[str, Set[str]] = {}
        self._initialization_order: List[str] = []

    def add_plugin_directory(self, directory: Path) -> None:
        """Add a directory to search for plugins."""
        if directory.exists() and directory.is_dir():
            self._plugin_directories.append(directory)

    def set_framework_context(self, context: Dict[str, Any]) -> None:
        """Set the framework context passed to plugins."""
        self._framework_context = context

    def discover_plugins(self) -> List[str]:
        """Discover plugins in the registered directories."""
        discovered_plugins = []

        for directory in self._plugin_directories:
            for plugin_file in directory.glob("*.py"):
                if plugin_file.stem.startswith("plugin_"):
                    discovered_plugins.append(plugin_file.stem)

        return discovered_plugins

    def load_plugin(
            self,
            plugin_name: str,
            plugin_path: Optional[Path] = None) -> bool:
        """
        Load a plugin from file or import path.

        Args:
            plugin_name: Name of the plugin
            plugin_path: Optional path to the plugin file

        Returns:
            True if plugin was loaded successfully, False otherwise
        """
        if plugin_name in self._plugins:
            return False  # Already loaded

        start_time = datetime.now()

        try:
            # Import the plugin module
            if plugin_path:
                spec = importlib.util.spec_from_file_location(
                    plugin_name, plugin_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            else:
                module = importlib.import_module(plugin_name)

            # Find the plugin class
            plugin_class = None
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                    issubclass(obj, SFMPlugin) and
                        obj is not SFMPlugin):
                    plugin_class = obj
                    break

            if not plugin_class:
                raise ValueError(f"No SFMPlugin class found in {plugin_name}")

            # Create plugin instance
            plugin_instance = plugin_class()
            metadata = plugin_instance.get_metadata()

            # Check dependencies
            if not self._check_dependencies(metadata.dependencies):
                raise ValueError(
                    f"Unmet dependencies for plugin {plugin_name}")

            # Initialize plugin
            plugin_instance.initialize(self._framework_context)

            # Create plugin info
            load_time = (datetime.now() - start_time).total_seconds() * 1000
            plugin_info = PluginInfo(
                metadata=metadata,
                plugin_instance=plugin_instance,
                status=PluginStatus.LOADED,
                loaded_at=start_time,
                load_time_ms=load_time
            )

            self._plugins[plugin_name] = plugin_info

            # Update dependency graph
            self._dependency_graph[plugin_name] = set(metadata.dependencies)

            return True

        except Exception as e:
            # Create error plugin info
            error_plugin_info = PluginInfo(
                metadata=PluginMetadata(
                    name=plugin_name,
                    version="unknown",
                    description="Failed to load",
                    author="unknown"
                ),
                plugin_instance=None,
                status=PluginStatus.ERROR,
                loaded_at=start_time,
                error_message=str(e)
            )

            self._plugins[plugin_name] = error_plugin_info
            return False

    def activate_plugin(self, plugin_name: str) -> bool:
        """
        Activate a loaded plugin.

        Args:
            plugin_name: Name of the plugin to activate

        Returns:
            True if plugin was activated successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            return False

        plugin_info = self._plugins[plugin_name]

        if plugin_info.status != PluginStatus.LOADED:
            return False

        try:
            plugin = plugin_info.plugin_instance

            # Register plugin resources
            for entity_type in plugin.register_entities():
                self._plugin_registry.register_entity_type(
                    entity_type, plugin_name)

            for relationship_kind in plugin.register_relationships():
                self._plugin_registry.register_relationship_kind(
                    relationship_kind, plugin_name)

            for name, analyzer in plugin.register_analyzers().items():
                self._plugin_registry.register_analyzer(
                    name, analyzer, plugin_name)

            for name, validator in plugin.register_validators().items():
                self._plugin_registry.register_validator(
                    name, validator, plugin_name)

            for event_type, handler in plugin.register_event_handlers().items():
                self._plugin_registry.register_event_handler(
                    event_type, handler, plugin_name)

            # Update plugin status
            plugin_info.status = PluginStatus.ACTIVATED
            plugin_info.activated_at = datetime.now()

            return True

        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            return False

    def deactivate_plugin(self, plugin_name: str) -> bool:
        """
        Deactivate an active plugin.

        Args:
            plugin_name: Name of the plugin to deactivate

        Returns:
            True if plugin was deactivated successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            return False

        plugin_info = self._plugins[plugin_name]

        if plugin_info.status != PluginStatus.ACTIVATED:
            return False

        try:
            # Unregister plugin resources
            self._plugin_registry.unregister_plugin_resources(plugin_name)

            # Cleanup plugin
            if plugin_info.plugin_instance:
                plugin_info.plugin_instance.cleanup()

            # Update plugin status
            plugin_info.status = PluginStatus.DEACTIVATED
            plugin_info.deactivated_at = datetime.now()

            return True

        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin completely.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if plugin was unloaded successfully, False otherwise
        """
        if plugin_name not in self._plugins:
            return False

        plugin_info = self._plugins[plugin_name]

        # Deactivate if active
        if plugin_info.status == PluginStatus.ACTIVATED:
            self.deactivate_plugin(plugin_name)

        # Cleanup plugin
        if plugin_info.plugin_instance:
            try:
                plugin_info.plugin_instance.cleanup()
            except Exception:
                pass  # Ignore cleanup errors during unload

        # Remove from registry
        del self._plugins[plugin_name]

        # Remove from dependency graph
        if plugin_name in self._dependency_graph:
            del self._dependency_graph[plugin_name]

        return True

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin."""
        return self._plugins.get(plugin_name)

    def list_plugins(
            self,
            status: Optional[PluginStatus] = None) -> List[PluginInfo]:
        """List all plugins, optionally filtered by status."""
        plugins = list(self._plugins.values())

        if status is not None:
            plugins = [p for p in plugins if p.status == status]

        return plugins

    def get_plugin_registry(self) -> PluginRegistry:
        """Get the plugin registry."""
        return self._plugin_registry

    def configure_plugin(self, plugin_name: str,
                         config: Dict[str, Any]) -> bool:
        """Configure a plugin with settings."""
        if plugin_name not in self._plugins:
            return False

        plugin_info = self._plugins[plugin_name]

        if not plugin_info.plugin_instance:
            return False

        try:
            plugin_info.plugin_instance.configure(config)
            return True
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            return False

    def get_plugin_health(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get health status of a plugin."""
        if plugin_name not in self._plugins:
            return None

        plugin_info = self._plugins[plugin_name]

        if not plugin_info.plugin_instance:
            return {"status": "error", "message": "Plugin not loaded"}

        try:
            return plugin_info.plugin_instance.get_health_status()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_plugin_metrics(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get metrics from a plugin."""
        if plugin_name not in self._plugins:
            return None

        plugin_info = self._plugins[plugin_name]

        if not plugin_info.plugin_instance:
            return None

        try:
            return plugin_info.plugin_instance.get_metrics()
        except Exception:
            return None

    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if all dependencies are satisfied."""
        for dep in dependencies:
            if dep not in self._plugins:
                return False

            plugin_info = self._plugins[dep]
            if plugin_info.status != PluginStatus.ACTIVATED:
                return False

        return True

    def _calculate_initialization_order(self) -> List[str]:
        """Calculate plugin initialization order based on dependencies."""
        # Topological sort of dependency graph
        visited = set()
        temp_visited = set()
        order = []

        def visit(plugin_name: str):
            if plugin_name in temp_visited:
                raise ValueError(
                    f"Circular dependency detected involving {plugin_name}")

            if plugin_name in visited:
                return

            temp_visited.add(plugin_name)

            # Visit dependencies first
            for dep in self._dependency_graph.get(plugin_name, []):
                visit(dep)

            temp_visited.remove(plugin_name)
            visited.add(plugin_name)
            order.append(plugin_name)

        # Visit all plugins
        for plugin_name in self._plugins:
            if plugin_name not in visited:
                visit(plugin_name)

        return order

    def activate_all_plugins(self) -> Dict[str, bool]:
        """Activate all loaded plugins in dependency order."""
        results = {}

        try:
            initialization_order = self._calculate_initialization_order()

            for plugin_name in initialization_order:
                if plugin_name in self._plugins:
                    plugin_info = self._plugins[plugin_name]
                    if plugin_info.status == PluginStatus.LOADED:
                        results[plugin_name] = self.activate_plugin(
                            plugin_name)
                    else:
                        results[plugin_name] = False

        except ValueError as e:
            # Circular dependency error
            for plugin_name in self._plugins:
                results[plugin_name] = False

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin manager statistics."""
        status_counts = {}
        for status in PluginStatus:
            status_counts[status.value] = len(
                [p for p in self._plugins.values() if p.status == status])

        return {
            "total_plugins": len(self._plugins),
            "status_counts": status_counts,
            "plugin_directories": [str(d) for d in self._plugin_directories],
            "registered_resources": self._plugin_registry.get_registered_resources()
        }


# Global plugin manager instance
_global_plugin_manager = PluginManager()


def get_global_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return _global_plugin_manager

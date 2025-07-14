"""
Dependency Injection Container Implementation for SFM Framework

This module implements a dependency injection container to manage dependencies
and improve testability, maintainability, and flexibility of the SFM framework.
"""

import inspect
import threading
from abc import ABC, abstractmethod
from typing import (
    TypeVar, Generic, Type, Any, Dict, List, Optional, Callable, 
    Union, get_type_hints, get_origin, get_args
)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from contextlib import contextmanager

T = TypeVar('T')


class LifecycleType(Enum):
    """Lifecycle types for dependency management."""
    TRANSIENT = "transient"  # New instance every time
    SINGLETON = "singleton"  # Single instance
    SCOPED = "scoped"  # Single instance per scope


@dataclass
class ServiceDescriptor:
    """Describes how a service should be created and managed."""
    service_type: Type
    implementation_type: Optional[Type] = None
    factory: Optional[Callable] = None
    instance: Optional[Any] = None
    lifecycle: LifecycleType = LifecycleType.TRANSIENT
    dependencies: List[Type] = field(default_factory=list)
    created_at: Optional[datetime] = None
    access_count: int = 0
    tags: List[str] = field(default_factory=list)


@dataclass
class ServiceContext:
    """Context information for service creation."""
    request_id: str
    created_at: datetime
    parent_context: Optional['ServiceContext'] = None
    services: Dict[Type, Any] = field(default_factory=dict)


class ServiceScope:
    """Scope for managing scoped services."""
    
    def __init__(self, container: 'DIContainer'):
        self.container = container
        self.services: Dict[Type, Any] = {}
        self.created_at = datetime.now()
        self.disposed = False
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service within this scope."""
        if self.disposed:
            raise RuntimeError("Scope has been disposed")
        
        if service_type in self.services:
            return self.services[service_type]
        
        # Create new service and cache it in this scope
        service = self.container._create_service(service_type, self)
        self.services[service_type] = service
        return service
    
    def dispose(self) -> None:
        """Dispose of all services in this scope."""
        if self.disposed:
            return
        
        # Dispose of services that implement IDisposable
        for service in self.services.values():
            if hasattr(service, 'dispose'):
                try:
                    service.dispose()
                except Exception:
                    pass  # Ignore disposal errors
        
        self.services.clear()
        self.disposed = True


class InjectionError(Exception):
    """Exception raised when dependency injection fails."""
    pass


class CircularDependencyError(InjectionError):
    """Exception raised when circular dependencies are detected."""
    pass


class DIContainer:
    """
    Dependency Injection Container for managing service dependencies.
    
    This container provides service registration, resolution, and lifecycle management
    with support for different service lifetimes and dependency injection patterns.
    """
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._singletons: Dict[Type, Any] = {}
        self._creation_stack: List[Type] = []
        self._lock = threading.RLock()
        self._interceptors: List[Callable[[Type, Any], Any]] = []
        self._decorators: List[Callable[[Type, Any], Any]] = []
        self._middleware: List[Callable[[Type, Dict[str, Any]], Dict[str, Any]]] = []
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._metrics = {
            "services_registered": 0,
            "services_created": 0,
            "singleton_hits": 0,
            "factory_calls": 0,
            "circular_dependencies": 0
        }
    
    def register_singleton(self, service_type: Type[T], instance: T) -> 'DIContainer':
        """Register a singleton instance."""
        with self._lock:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                instance=instance,
                lifecycle=LifecycleType.SINGLETON,
                created_at=datetime.now()
            )
            
            self._services[service_type] = descriptor
            self._singletons[service_type] = instance
            self._metrics["services_registered"] += 1
            
            self._emit_event("service_registered", {
                "service_type": service_type.__name__,
                "lifecycle": LifecycleType.SINGLETON.value
            })
            
            return self
    
    def register_transient(self, service_type: Type[T], 
                          implementation_type: Optional[Type[T]] = None) -> 'DIContainer':
        """Register a transient service (new instance every time)."""
        with self._lock:
            impl_type = implementation_type or service_type
            dependencies = self._analyze_dependencies(impl_type)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifecycle=LifecycleType.TRANSIENT,
                dependencies=dependencies,
                created_at=datetime.now()
            )
            
            self._services[service_type] = descriptor
            self._metrics["services_registered"] += 1
            
            self._emit_event("service_registered", {
                "service_type": service_type.__name__,
                "implementation_type": impl_type.__name__,
                "lifecycle": LifecycleType.TRANSIENT.value
            })
            
            return self
    
    def register_scoped(self, service_type: Type[T], 
                       implementation_type: Optional[Type[T]] = None) -> 'DIContainer':
        """Register a scoped service (single instance per scope)."""
        with self._lock:
            impl_type = implementation_type or service_type
            dependencies = self._analyze_dependencies(impl_type)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                implementation_type=impl_type,
                lifecycle=LifecycleType.SCOPED,
                dependencies=dependencies,
                created_at=datetime.now()
            )
            
            self._services[service_type] = descriptor
            self._metrics["services_registered"] += 1
            
            self._emit_event("service_registered", {
                "service_type": service_type.__name__,
                "implementation_type": impl_type.__name__,
                "lifecycle": LifecycleType.SCOPED.value
            })
            
            return self
    
    def register_factory(self, service_type: Type[T], 
                        factory: Callable[[], T],
                        lifecycle: LifecycleType = LifecycleType.TRANSIENT) -> 'DIContainer':
        """Register a factory function for creating services."""
        with self._lock:
            dependencies = self._analyze_factory_dependencies(factory)
            
            descriptor = ServiceDescriptor(
                service_type=service_type,
                factory=factory,
                lifecycle=lifecycle,
                dependencies=dependencies,
                created_at=datetime.now()
            )
            
            self._services[service_type] = descriptor
            self._metrics["services_registered"] += 1
            
            self._emit_event("service_registered", {
                "service_type": service_type.__name__,
                "factory": factory.__name__,
                "lifecycle": lifecycle.value
            })
            
            return self
    
    def register_instance(self, service_type: Type[T], instance: T,
                         lifecycle: LifecycleType = LifecycleType.SINGLETON) -> 'DIContainer':
        """Register a specific instance."""
        with self._lock:
            descriptor = ServiceDescriptor(
                service_type=service_type,
                instance=instance,
                lifecycle=lifecycle,
                created_at=datetime.now()
            )
            
            self._services[service_type] = descriptor
            
            if lifecycle == LifecycleType.SINGLETON:
                self._singletons[service_type] = instance
            
            self._metrics["services_registered"] += 1
            
            self._emit_event("service_registered", {
                "service_type": service_type.__name__,
                "lifecycle": lifecycle.value
            })
            
            return self
    
    def get(self, service_type: Type[T]) -> T:
        """Get a service instance."""
        with self._lock:
            return self._get_service(service_type)
    
    def try_get(self, service_type: Type[T]) -> Optional[T]:
        """Try to get a service instance, return None if not found."""
        try:
            return self.get(service_type)
        except InjectionError:
            return None
    
    def _get_service(self, service_type: Type[T], scope: Optional[ServiceScope] = None) -> T:
        """Internal method to get a service instance."""
        if service_type not in self._services:
            raise InjectionError(f"Service {service_type.__name__} is not registered")
        
        descriptor = self._services[service_type]
        
        # Check for circular dependencies
        if service_type in self._creation_stack:
            self._metrics["circular_dependencies"] += 1
            dependency_chain = " -> ".join(cls.__name__ for cls in self._creation_stack)
            raise CircularDependencyError(
                f"Circular dependency detected: {dependency_chain} -> {service_type.__name__}"
            )
        
        # Handle singleton
        if descriptor.lifecycle == LifecycleType.SINGLETON:
            if service_type in self._singletons:
                descriptor.access_count += 1
                self._metrics["singleton_hits"] += 1
                return self._apply_interceptors(service_type, self._singletons[service_type])
            
            # Create singleton instance
            instance = self._create_service(service_type, scope)
            self._singletons[service_type] = instance
            return instance
        
        # Handle scoped
        if descriptor.lifecycle == LifecycleType.SCOPED:
            if scope and service_type in scope.services:
                descriptor.access_count += 1
                return self._apply_interceptors(service_type, scope.services[service_type])
            
            # Create scoped instance
            instance = self._create_service(service_type, scope)
            if scope:
                scope.services[service_type] = instance
            return instance
        
        # Handle transient
        return self._create_service(service_type, scope)
    
    def _create_service(self, service_type: Type[T], scope: Optional[ServiceScope] = None) -> T:
        """Create a new service instance."""
        descriptor = self._services[service_type]
        
        # Add to creation stack for circular dependency detection
        self._creation_stack.append(service_type)
        
        try:
            # Apply middleware
            context = {"service_type": service_type, "scope": scope}
            for middleware in self._middleware:
                context = middleware(service_type, context)
            
            # Create instance
            if descriptor.instance is not None:
                instance = descriptor.instance
            elif descriptor.factory is not None:
                instance = self._invoke_factory(descriptor.factory, scope)
                self._metrics["factory_calls"] += 1
            elif descriptor.implementation_type is not None:
                instance = self._create_instance(descriptor.implementation_type, scope)
            else:
                instance = self._create_instance(service_type, scope)
            
            # Apply decorators
            for decorator in self._decorators:
                instance = decorator(service_type, instance)
            
            # Apply interceptors
            instance = self._apply_interceptors(service_type, instance)
            
            descriptor.access_count += 1
            self._metrics["services_created"] += 1
            
            self._emit_event("service_created", {
                "service_type": service_type.__name__,
                "lifecycle": descriptor.lifecycle.value
            })
            
            return instance
            
        finally:
            # Remove from creation stack
            self._creation_stack.pop()
    
    def _create_instance(self, implementation_type: Type[T], scope: Optional[ServiceScope] = None) -> T:
        """Create an instance by invoking the constructor with dependencies."""
        # Get constructor signature
        constructor = implementation_type.__init__
        sig = inspect.signature(constructor)
        
        # Prepare arguments
        args = []
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Get parameter type
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                # Try to get type from type hints
                type_hints = get_type_hints(constructor)
                param_type = type_hints.get(param_name, Any)
            
            # Skip if type is Any or not a class
            if param_type == Any or not isinstance(param_type, type):
                continue
            
            # Resolve dependency
            if param.default == inspect.Parameter.empty:
                # Required parameter
                dependency = self._get_service(param_type, scope)
                if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    args.append(dependency)
                else:
                    kwargs[param_name] = dependency
            else:
                # Optional parameter
                try:
                    dependency = self._get_service(param_type, scope)
                    if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                        args.append(dependency)
                    else:
                        kwargs[param_name] = dependency
                except InjectionError:
                    # Use default value
                    pass
        
        # Create instance
        return implementation_type(*args, **kwargs)
    
    def _invoke_factory(self, factory: Callable, scope: Optional[ServiceScope] = None) -> Any:
        """Invoke a factory function with dependency injection."""
        sig = inspect.signature(factory)
        
        # Prepare arguments
        args = []
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            # Get parameter type
            param_type = param.annotation
            if param_type == inspect.Parameter.empty:
                # Try to get type from type hints
                type_hints = get_type_hints(factory)
                param_type = type_hints.get(param_name, Any)
            
            # Skip if type is Any or not a class
            if param_type == Any or not isinstance(param_type, type):
                continue
            
            # Resolve dependency
            if param.default == inspect.Parameter.empty:
                # Required parameter
                dependency = self._get_service(param_type, scope)
                if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                    args.append(dependency)
                else:
                    kwargs[param_name] = dependency
            else:
                # Optional parameter
                try:
                    dependency = self._get_service(param_type, scope)
                    if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
                        args.append(dependency)
                    else:
                        kwargs[param_name] = dependency
                except InjectionError:
                    # Use default value
                    pass
        
        # Invoke factory
        return factory(*args, **kwargs)
    
    def _analyze_dependencies(self, service_type: Type) -> List[Type]:
        """Analyze dependencies of a service type."""
        dependencies = []
        
        try:
            constructor = service_type.__init__
            sig = inspect.signature(constructor)
            type_hints = get_type_hints(constructor)
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                param_type = param.annotation
                if param_type == inspect.Parameter.empty:
                    param_type = type_hints.get(param_name, Any)
                
                if param_type != Any and isinstance(param_type, type):
                    dependencies.append(param_type)
        
        except Exception:
            pass  # Ignore analysis errors
        
        return dependencies
    
    def _analyze_factory_dependencies(self, factory: Callable) -> List[Type]:
        """Analyze dependencies of a factory function."""
        dependencies = []
        
        try:
            sig = inspect.signature(factory)
            type_hints = get_type_hints(factory)
            
            for param_name, param in sig.parameters.items():
                param_type = param.annotation
                if param_type == inspect.Parameter.empty:
                    param_type = type_hints.get(param_name, Any)
                
                if param_type != Any and isinstance(param_type, type):
                    dependencies.append(param_type)
        
        except Exception:
            pass  # Ignore analysis errors
        
        return dependencies
    
    def _apply_interceptors(self, service_type: Type, instance: Any) -> Any:
        """Apply interceptors to a service instance."""
        for interceptor in self._interceptors:
            instance = interceptor(service_type, instance)
        return instance
    
    def _emit_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Emit an event to registered handlers."""
        if event_name in self._event_handlers:
            for handler in self._event_handlers[event_name]:
                try:
                    handler(data)
                except Exception:
                    pass  # Ignore handler errors
    
    def add_interceptor(self, interceptor: Callable[[Type, Any], Any]) -> 'DIContainer':
        """Add an interceptor to modify service instances."""
        self._interceptors.append(interceptor)
        return self
    
    def add_decorator(self, decorator: Callable[[Type, Any], Any]) -> 'DIContainer':
        """Add a decorator to modify service instances."""
        self._decorators.append(decorator)
        return self
    
    def add_middleware(self, middleware: Callable[[Type, Dict[str, Any]], Dict[str, Any]]) -> 'DIContainer':
        """Add middleware to modify service creation context."""
        self._middleware.append(middleware)
        return self
    
    def add_event_handler(self, event_name: str, handler: Callable[[Dict[str, Any]], None]) -> 'DIContainer':
        """Add an event handler."""
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
        return self
    
    def create_scope(self) -> ServiceScope:
        """Create a new service scope."""
        return ServiceScope(self)
    
    @contextmanager
    def scope(self):
        """Context manager for service scopes."""
        service_scope = self.create_scope()
        try:
            yield service_scope
        finally:
            service_scope.dispose()
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def get_service_info(self, service_type: Type) -> Optional[ServiceDescriptor]:
        """Get information about a registered service."""
        return self._services.get(service_type)
    
    def list_services(self) -> List[ServiceDescriptor]:
        """List all registered services."""
        return list(self._services.values())
    
    def unregister(self, service_type: Type) -> bool:
        """Unregister a service type."""
        with self._lock:
            if service_type in self._services:
                del self._services[service_type]
                
                # Remove singleton if exists
                if service_type in self._singletons:
                    del self._singletons[service_type]
                
                self._emit_event("service_unregistered", {
                    "service_type": service_type.__name__
                })
                
                return True
            return False
    
    def clear(self) -> None:
        """Clear all registered services."""
        with self._lock:
            self._services.clear()
            self._singletons.clear()
            self._creation_stack.clear()
            
            # Reset metrics
            self._metrics = {
                "services_registered": 0,
                "services_created": 0,
                "singleton_hits": 0,
                "factory_calls": 0,
                "circular_dependencies": 0
            }
            
            self._emit_event("container_cleared", {})
    
    def validate_configuration(self) -> List[str]:
        """Validate the container configuration and return any issues."""
        issues = []
        
        # Check for missing dependencies
        for service_type, descriptor in self._services.items():
            for dependency in descriptor.dependencies:
                if dependency not in self._services:
                    issues.append(
                        f"Service {service_type.__name__} depends on unregistered service {dependency.__name__}"
                    )
        
        # Check for circular dependencies
        for service_type in self._services:
            try:
                self._check_circular_dependencies(service_type, set())
            except CircularDependencyError as e:
                issues.append(str(e))
        
        return issues
    
    def _check_circular_dependencies(self, service_type: Type, visited: set) -> None:
        """Check for circular dependencies starting from a service type."""
        if service_type in visited:
            raise CircularDependencyError(f"Circular dependency detected involving {service_type.__name__}")
        
        if service_type not in self._services:
            return
        
        visited.add(service_type)
        
        descriptor = self._services[service_type]
        for dependency in descriptor.dependencies:
            self._check_circular_dependencies(dependency, visited.copy())
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get container metrics."""
        return {
            **self._metrics,
            "registered_services": len(self._services),
            "singleton_instances": len(self._singletons),
            "interceptors": len(self._interceptors),
            "decorators": len(self._decorators),
            "middleware": len(self._middleware),
            "event_handlers": sum(len(handlers) for handlers in self._event_handlers.values())
        }
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the dependency graph as a dictionary."""
        graph = {}
        
        for service_type, descriptor in self._services.items():
            dependencies = [dep.__name__ for dep in descriptor.dependencies]
            graph[service_type.__name__] = dependencies
        
        return graph


# Global container instance
_global_container = DIContainer()


def get_global_container() -> DIContainer:
    """Get the global DI container instance."""
    return _global_container


def inject(service_type: Type[T]) -> T:
    """Inject a service from the global container."""
    return _global_container.get(service_type)


def configure_global_container(configurator: Callable[[DIContainer], None]) -> None:
    """Configure the global container."""
    configurator(_global_container)


# Example usage and utilities
class ServiceA:
    def __init__(self):
        self.name = "Service A"
    
    def do_something(self):
        return f"{self.name} did something"


class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a
        self.name = "Service B"
    
    def do_something(self):
        return f"{self.name} used {self.service_a.do_something()}"


class ServiceC:
    def __init__(self, service_a: ServiceA, service_b: ServiceB):
        self.service_a = service_a
        self.service_b = service_b
        self.name = "Service C"
    
    def do_something(self):
        return f"{self.name} coordinated {self.service_a.name} and {self.service_b.name}"


def example_configuration():
    """Example of how to configure the DI container."""
    container = DIContainer()
    
    # Register services
    container.register_singleton(ServiceA, ServiceA())
    container.register_transient(ServiceB)
    container.register_scoped(ServiceC)
    
    # Register with factory
    container.register_factory(
        str,
        lambda: "Hello from factory",
        LifecycleType.SINGLETON
    )
    
    # Add interceptor
    def logging_interceptor(service_type: Type, instance: Any) -> Any:
        print(f"Created instance of {service_type.__name__}")
        return instance
    
    container.add_interceptor(logging_interceptor)
    
    return container
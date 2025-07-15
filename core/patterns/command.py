"""
Command Pattern Implementation for SFM Framework

This module implements the Command pattern to provide undo/redo functionality
for graph operations, allowing users to reverse complex operations and maintain
command history.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass

from core.base_nodes import Node
from core.relationships import Relationship

# Use TYPE_CHECKING to avoid circular imports
if TYPE_CHECKING:
    from core.graph import SFMGraph


class Command(ABC):
    """Abstract base class for all commands."""
    
    def __init__(self, command_id: Optional[uuid.UUID] = None):
        self.command_id = command_id or uuid.uuid4()
        self.timestamp = datetime.now()
        self.executed = False
        self.undone = False
    
    @abstractmethod
    def execute(self) -> Any:
        """Execute the command and return the result."""
        pass
    
    @abstractmethod
    def undo(self) -> Any:
        """Undo the command and return the result."""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """Check if the command can be undone."""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Get a human-readable description of the command."""
        pass


@dataclass
class CommandMetadata:
    """Metadata for command execution."""
    command_id: uuid.UUID
    command_type: str
    description: str
    timestamp: datetime
    executed: bool
    undone: bool
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class AddNodeCommand(Command):
    """Command to add a node to the graph."""
    
    def __init__(self, graph: "SFMGraph", node: Node):
        super().__init__()
        self.graph = graph
        self.node = node
        self.node_was_added = False
    
    def execute(self) -> Node:
        """Add the node to the graph."""
        if self.executed and not self.undone:
            raise RuntimeError("Command already executed")
        
        # Use the graph's add_node method
        result = self.graph.add_node(self.node)
        self.executed = True
        self.undone = False
        self.node_was_added = True
        return result
    
    def undo(self) -> bool:
        """Remove the node from the graph."""
        if not self.executed or self.undone:
            return False
        
        if not self.node_was_added:
            return False
        
        # Remove the node from the appropriate collection
        collection_name = self.graph._node_registry.get_collection_name(self.node)  # type: ignore  # Protected access needed for command pattern
        collection = getattr(self.graph, collection_name)
        
        if self.node.id in collection:
            del collection[self.node.id]
            # Also remove from node index if it exists
            if hasattr(self.graph, '_node_index') and self.node.id in self.graph._node_index:  # type: ignore  # Protected access needed for command pattern
                del self.graph._node_index[self.node.id]  # type: ignore  # Protected access needed for command pattern
            self.undone = True
            return True
        
        return False
    
    def can_undo(self) -> bool:
        """Check if this command can be undone."""
        return self.executed and not self.undone and self.node_was_added
    
    def get_description(self) -> str:
        """Get a description of this command."""
        return f"Add node '{self.node.label}' ({type(self.node).__name__})"


class RemoveNodeCommand(Command):
    """Command to remove a node from the graph."""
    
    def __init__(self, graph: "SFMGraph", node_id: uuid.UUID):
        super().__init__()
        self.graph = graph
        self.node_id = node_id
        self.removed_node: Optional[Node] = None
        self.removed_relationships: List[Relationship] = []
    
    def execute(self) -> bool:
        """Remove the node from the graph."""
        if self.executed and not self.undone:
            raise RuntimeError("Command already executed")
        
        # Find the node first
        node = self.graph.get_node_by_id(self.node_id)
        if not node:
            return False
        
        self.removed_node = node
        
        # Store relationships that will be removed
        self.removed_relationships = self.graph.get_node_relationships(self.node_id)
        
        # Remove relationships first
        for rel in self.removed_relationships:
            if rel.id in self.graph.relationships:
                del self.graph.relationships[rel.id]
        
        # Remove the node
        collection_name = self.graph._node_registry.get_collection_name(node)  # type: ignore  # Protected access needed for command pattern
        collection = getattr(self.graph, collection_name)
        
        if self.node_id in collection:
            del collection[self.node_id]
            # Also remove from node index if it exists
            if hasattr(self.graph, '_node_index') and self.node_id in self.graph._node_index:  # type: ignore  # Protected access needed for command pattern
                del self.graph._node_index[self.node_id]  # type: ignore  # Protected access needed for command pattern
            
            self.executed = True
            self.undone = False
            return True
        
        return False
    
    def undo(self) -> bool:
        """Restore the node to the graph."""
        if not self.executed or self.undone or not self.removed_node:
            return False
        
        # Restore the node
        result = self.graph.add_node(self.removed_node)
        
        # Restore relationships
        for rel in self.removed_relationships:
            self.graph.relationships[rel.id] = rel
        
        self.undone = True
        return result is not None  # type: ignore  # May return None in some cases
    
    def can_undo(self) -> bool:
        """Check if this command can be undone."""
        return self.executed and not self.undone and self.removed_node is not None
    
    def get_description(self) -> str:
        """Get a description of this command."""
        node_label = self.removed_node.label if self.removed_node else "unknown"
        return f"Remove node '{node_label}' ({self.node_id})"


class AddRelationshipCommand(Command):
    """Command to add a relationship to the graph."""
    
    def __init__(self, graph: "SFMGraph", relationship: Relationship):
        super().__init__()
        self.graph = graph
        self.relationship = relationship
        self.relationship_was_added = False
    
    def execute(self) -> Relationship:
        """Add the relationship to the graph."""
        if self.executed and not self.undone:
            raise RuntimeError("Command already executed")
        
        result = self.graph.add_relationship(self.relationship)
        self.executed = True
        self.undone = False
        self.relationship_was_added = True
        return result
    
    def undo(self) -> bool:
        """Remove the relationship from the graph."""
        if not self.executed or self.undone:
            return False
        
        if not self.relationship_was_added:
            return False
        
        if self.relationship.id in self.graph.relationships:
            del self.graph.relationships[self.relationship.id]
            # Clear relationship cache
            if hasattr(self.graph, '_clear_relationship_cache'):
                self.graph._clear_relationship_cache()  # type: ignore  # Protected access needed for command pattern
            self.undone = True
            return True
        
        return False
    
    def can_undo(self) -> bool:
        """Check if this command can be undone."""
        return self.executed and not self.undone and self.relationship_was_added
    
    def get_description(self) -> str:
        """Get a description of this command."""
        return f"Add relationship {self.relationship.source_id} -> {self.relationship.target_id} ({self.relationship.kind})"


class RemoveRelationshipCommand(Command):
    """Command to remove a relationship from the graph."""
    
    def __init__(self, graph: "SFMGraph", relationship_id: uuid.UUID):
        super().__init__()
        self.graph = graph
        self.relationship_id = relationship_id
        self.removed_relationship: Optional[Relationship] = None
    
    def execute(self) -> bool:
        """Remove the relationship from the graph."""
        if self.executed and not self.undone:
            raise RuntimeError("Command already executed")
        
        if self.relationship_id in self.graph.relationships:
            self.removed_relationship = self.graph.relationships[self.relationship_id]
            del self.graph.relationships[self.relationship_id]
            # Clear relationship cache
            if hasattr(self.graph, '_clear_relationship_cache'):
                self.graph._clear_relationship_cache()  # type: ignore  # Protected access needed for command pattern
            self.executed = True
            self.undone = False
            return True
        
        return False
    
    def undo(self) -> bool:
        """Restore the relationship to the graph."""
        if not self.executed or self.undone or not self.removed_relationship:
            return False
        
        self.graph.relationships[self.relationship_id] = self.removed_relationship
        # Clear relationship cache
        if hasattr(self.graph, '_clear_relationship_cache'):
            self.graph._clear_relationship_cache()  # type: ignore  # Protected access needed for command pattern
        self.undone = True
        return True
    
    def can_undo(self) -> bool:
        """Check if this command can be undone."""
        return self.executed and not self.undone and self.removed_relationship is not None
    
    def get_description(self) -> str:
        """Get a description of this command."""
        if self.removed_relationship:
            return f"Remove relationship {self.removed_relationship.source_id} -> {self.removed_relationship.target_id}"
        return f"Remove relationship {self.relationship_id}"


class MacroCommand(Command):
    """Command that executes multiple commands as a single unit."""
    
    def __init__(self, commands: List[Command], description: str = "Macro command"):
        super().__init__()
        self.commands = commands
        self.description = description
        self.executed_commands: List[Command] = []
    
    def execute(self) -> List[Any]:
        """Execute all commands in sequence."""
        if self.executed and not self.undone:
            raise RuntimeError("Command already executed")
        
        results: List[Any] = []
        self.executed_commands.clear()
        
        for command in self.commands:
            try:
                result = command.execute()
                results.append(result)
                self.executed_commands.append(command)
            except Exception as e:
                # If any command fails, undo all previously executed commands
                for executed_cmd in reversed(self.executed_commands):
                    if executed_cmd.can_undo():
                        executed_cmd.undo()
                raise e
        
        self.executed = True
        self.undone = False
        return results
    
    def undo(self) -> bool:
        """Undo all commands in reverse order."""
        if not self.executed or self.undone:
            return False
        
        # Undo in reverse order
        success = True
        for command in reversed(self.executed_commands):
            if command.can_undo():
                if not command.undo():
                    success = False
        
        if success:
            self.undone = True
        
        return success
    
    def can_undo(self) -> bool:
        """Check if all commands can be undone."""
        if not self.executed or self.undone:
            return False
        
        return all(cmd.can_undo() for cmd in self.executed_commands)
    
    def get_description(self) -> str:
        """Get a description of this macro command."""
        return self.description


class CommandManager:
    """
    Manages command execution and history for undo/redo operations.
    
    This class maintains a history of executed commands and provides
    methods to undo and redo operations.
    """
    
    def __init__(self, max_history: int = 100):
        self._history: List[Command] = []
        self._current_index = -1
        self._max_history = max_history
        self._command_metadata: Dict[uuid.UUID, CommandMetadata] = {}
    
    def execute(self, command: Command) -> Any:
        """Execute a command and add it to the history."""
        start_time = datetime.now()
        
        try:
            result = command.execute()
            
            # Remove any commands after the current index (for redo functionality)
            if self._current_index < len(self._history) - 1:
                self._history = self._history[:self._current_index + 1]
            
            # Add command to history
            self._add_to_history(command)
            
            # Record metadata
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._command_metadata[command.command_id] = CommandMetadata(
                command_id=command.command_id,
                command_type=type(command).__name__,
                description=command.get_description(),
                timestamp=command.timestamp,
                executed=True,
                undone=False,
                execution_time_ms=execution_time
            )
            
            return result
            
        except Exception as e:
            # Record error in metadata
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            self._command_metadata[command.command_id] = CommandMetadata(
                command_id=command.command_id,
                command_type=type(command).__name__,
                description=command.get_description(),
                timestamp=command.timestamp,
                executed=False,
                undone=False,
                execution_time_ms=execution_time,
                error_message=str(e)
            )
            raise
    
    def undo(self) -> bool:
        """Undo the last command."""
        if not self.can_undo():
            return False
        
        command = self._history[self._current_index]
        success = command.undo()
        
        if success:
            self._current_index -= 1
            # Update metadata
            if command.command_id in self._command_metadata:
                self._command_metadata[command.command_id].undone = True
        
        return success
    
    def redo(self) -> bool:
        """Redo the next command."""
        if not self.can_redo():
            return False
        
        command = self._history[self._current_index + 1]
        success = command.execute()
        
        if success:
            self._current_index += 1
            # Update metadata
            if command.command_id in self._command_metadata:
                self._command_metadata[command.command_id].undone = False
        
        return success
    
    def can_undo(self) -> bool:
        """Check if there are commands that can be undone."""
        return (self._current_index >= 0 and 
                self._current_index < len(self._history) and
                self._history[self._current_index].can_undo())
    
    def can_redo(self) -> bool:
        """Check if there are commands that can be redone."""
        return (self._current_index + 1 < len(self._history) and
                self._history[self._current_index + 1].can_undo())
    
    def _add_to_history(self, command: Command) -> None:
        """Add a command to the history."""
        self._history.append(command)
        self._current_index += 1
        
        # Maintain history size limit
        if len(self._history) > self._max_history:
            # Remove the oldest command
            removed_command = self._history.pop(0)
            self._current_index -= 1
            # Remove metadata for removed command
            if removed_command.command_id in self._command_metadata:
                del self._command_metadata[removed_command.command_id]
    
    def get_history(self) -> List[CommandMetadata]:
        """Get the command history metadata."""
        return [self._command_metadata[cmd.command_id] for cmd in self._history
                if cmd.command_id in self._command_metadata]
    
    def get_undo_stack(self) -> List[CommandMetadata]:
        """Get commands that can be undone."""
        return [self._command_metadata[cmd.command_id] for cmd in self._history[:self._current_index + 1]
                if cmd.command_id in self._command_metadata]
    
    def get_redo_stack(self) -> List[CommandMetadata]:
        """Get commands that can be redone."""
        return [self._command_metadata[cmd.command_id] for cmd in self._history[self._current_index + 1:]
                if cmd.command_id in self._command_metadata]
    
    def clear_history(self) -> None:
        """Clear the command history."""
        self._history.clear()
        self._current_index = -1
        self._command_metadata.clear()
    
    def get_current_command(self) -> Optional[Command]:
        """Get the current command in the history."""
        if 0 <= self._current_index < len(self._history):
            return self._history[self._current_index]
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about command execution."""
        total_commands = len(self._history)
        successful_commands = sum(1 for cmd in self._history if cmd.executed and not cmd.undone)
        failed_commands = len([meta for meta in self._command_metadata.values() if meta.error_message])
        
        avg_execution_time = None
        if self._command_metadata:
            execution_times = [meta.execution_time_ms for meta in self._command_metadata.values() 
                             if meta.execution_time_ms is not None]
            if execution_times:
                avg_execution_time = sum(execution_times) / len(execution_times)
        
        return {
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "failed_commands": failed_commands,
            "current_index": self._current_index,
            "can_undo": self.can_undo(),
            "can_redo": self.can_redo(),
            "avg_execution_time_ms": avg_execution_time,
            "history_size": len(self._history),
            "max_history_size": self._max_history
        }
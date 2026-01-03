# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Iterable, Self

from ..core import Pid, State


@dataclass(frozen=True)
class Configuration:
    """Represents the state of all processes in a distributed system at a given time.
    
    A configuration maps each process identifier (PID) to its current state.
    
    Attributes:
        states: A dictionary mapping process identifiers to their current states.
    """
    states: dict[Pid, State]

    def updated(self, states: Iterable[State]) -> Self:
        """Create a new configuration with updated states.
        
        Args:
            states: An iterable of new states that should replace the old ones.
        
        Returns:
            A new Configuration with the updated states.
        """
        new_states = {state.pid: state for state in states}
        updated_states = {pid: new_states.get(pid, state) for pid, state in self.states.items()}
        return Configuration(updated_states)

    def processes(self) -> Iterable[Pid]:
        """Get the identifiers of all processes in the configuration.
        
        Returns:
            An iterable of process identifiers, sorted in ascending order.
        """
        return sorted(self.states.keys())
    
    def changed_from(self, other: Self) -> Iterable[Pid]:
        """Get the identifiers of processes that have changed between two configurations.
        
        Args:
            other: The previous configuration to compare against.
        
        Returns:
            An iterable of process identifiers whose states have changed.
        """
        return (pid for pid in self.processes() if pid in other and self.states[pid] != other.states[pid])
    
    def __getitem__(self, pid: Pid) -> State:
        """Get the state of a process by its identifier.
        
        Args:
            pid: The process identifier.
        
        Returns:
            The state of the specified process.
        """
        return self.states.get(pid)

    def __contains__(self, pid: Pid) -> bool:
        """Check if a process exists in the configuration.
        
        Args:
            pid: The process identifier to check.
        
        Returns:
            True if the process is in the configuration, False otherwise.
        """
        return pid in self.states

    def __iter__(self) -> Iterable[State]:
        """Iterate over the states in the configuration.
        
        Returns:
            An iterator over all process states in the configuration.
        """
        return iter(self.states.values())
    
    def __len__(self) -> int:
        """Get the number of processes in the configuration.
        
        Returns:
            The number of process states in the configuration.
        """
        return len(self.states)

    @classmethod
    def from_states(cls, states: Iterable[State]) -> Self:
        """Create a configuration from a collection of process states.
        
        Args:
            states: An iterable of State objects with associated process identifiers.
        
        Returns:
            A new Configuration mapping each process to its state.
        """
        return cls(states={state.pid: state for state in states})

    def __str__(self) -> str:
        """Get a string representation of the configuration.
        
        Returns:
            A formatted string showing all process states in the configuration.
        """
        states = '\n  '.join(str(self.states[p]) for p in sorted(self.states.keys()) )
        return f"Configuration:\n  {states if states else '<empty>'}"

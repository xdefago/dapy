# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, Optional, Sequence, TypeVar

from .event import Event
from .pid import Pid
from .state import State
from .system import System

StateT = TypeVar('StateT', bound=State)


@dataclass(frozen=True)
class Algorithm(ABC, Generic[StateT]):
    """Abstract base class for distributed algorithms.
    
    This class defines the interface for distributed algorithms that can be
    simulated using the dapy framework.
    
    Algorithm Naming and Description:
        Subclasses can override class variables `algorithm_name` and `algorithm_description`
        to provide metadata that appears in traces and the viewer UI:
        - If `algorithm_name` is None, the class name is used (via the `name` property)
        - If `algorithm_description` is None or empty, it's extracted from the class
          docstring, excluding API documentation sections (via the `description` property)
    
    Class Variables:
        algorithm_name: Optional name for the algorithm. If None, the class name is used.
        algorithm_description: Optional description. If None, extracted from docstring.
    
    Attributes:
        system: The distributed system in which the algorithm is executed.
    """
    system: System
    
    # Class variables that can be overridden in subclasses
    algorithm_name: Optional[str] = None
    algorithm_description: Optional[str] = None

    @property
    def name(self) -> str:
        """Return the name of the algorithm.
        
        Uses the class variable algorithm_name if set in a subclass,
        otherwise returns the class name.
        
        Returns:
            The algorithm name.
        """
        # Get the class-level algorithm_name from the concrete subclass
        cls_name = type(self).algorithm_name
        if cls_name is not None:
            return cls_name
        return type(self).__name__
    
    @property
    def description(self) -> str:
        """Return the description of the algorithm.
        
        Uses the class variable algorithm_description if set in a subclass.
        If None or empty, extracts from the class docstring (excluding the
        Attributes section and other API documentation sections).
        If no docstring exists, returns an empty string.
        
        Returns:
            The algorithm description.
        """
        # Get the class-level algorithm_description from the concrete subclass
        cls_desc = type(self).algorithm_description
        
        # If explicitly set and not empty, use it
        if cls_desc:
            return cls_desc
        
        # Otherwise, extract from docstring
        docstring = type(self).__doc__
        if not docstring:
            return ""
        
        # Remove attributes section and subsequent API documentation
        lines = docstring.strip().split('\n')
        result_lines = []
        for line in lines:
            stripped = line.strip()
            # Stop at common API documentation headers
            if stripped.lower().startswith(('attributes:', 'args:', 'arguments:', 
                                           'returns:', 'return:', 'raises:', 
                                           'raise:', 'yields:', 'yield:', 
                                           'examples:', 'example:', 'note:', 
                                           'notes:', 'see also:', 'references:', 
                                           'warning:', 'warnings:')):
                break
            result_lines.append(line)
        
        return '\n'.join(result_lines).strip()
    
    #
    # Mandatory method: given a process id, create and return the initial state of that process.
    #
    @abstractmethod
    def initial_state(self, pid: Pid) -> StateT:
        """Create the initial state for a process.
        
        Args:
            pid: The process identifier for which to create the initial state.
        
        Returns:
            The initial state for the given process.
        """
        """
        Initialize the algorithm with the given system.
        """
        pass
    
    #
    # Optional method: handle the start of the algorithm.
    # Override this method only if your algorithms needs to do something specific at the start of the execution.
    #
    def on_start(self, init_state: StateT) -> tuple[StateT, Sequence[Event]]:
        """
        Handle the start of the algorithm.
        """
        return init_state, []
    
    #
    # Mandatory method:
    # given the state of a process and an event (signal or message) applied to it,
    # return the new state of the process and a list of events to be scheduled.
    #    
    @abstractmethod
    def on_event(self, old_state: StateT, event: Event) -> tuple[StateT, Sequence[Event]]:
        """
        Handle an event.
        Given the old state and the event, return the new state and a list of events to be sent.
        """
        pass


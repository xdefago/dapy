from abc import ABC, abstractmethod
from dataclasses import dataclass

from .event import Event
from .pid import Pid
from .state import State
from .system import System


@dataclass(frozen=True)
class Algorithm(ABC):
    """Abstract base class for distributed algorithms.
    
    This class defines the interface for distributed algorithms that can be
    simulated using the dapy framework.
    
    Attributes:
        system: The distributed system in which the algorithm is executed.
    """
    system: System

    #
    # Optional method: return the name of the algorithm.
    # Override this method if you want to provide a specific name for the algorithm.
    # By default, it returns the class name.
    #
    @property
    def name(self) -> str:
        """
        Return the name of the algorithm.
        """
        return type(self).__name__
    
    #
    # Mandatory method: given a process id, create and return the initial state of that process.
    #
    @abstractmethod
    def initial_state(self, pid: Pid) -> State:
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
    def on_start(self, init_state: State) -> tuple[State, list[Event]]:
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
    def on_event(self, old_state: State, event: Event) -> tuple[State, list[Event]]:
        """
        Handle an event.
        Given the old state and the event, return the new state and a list of events to be sent.
        """
        pass


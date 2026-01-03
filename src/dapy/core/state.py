from abc import ABC
from dataclasses import dataclass
from typing import Any, Iterable, Optional, Self

from .pid import Pid


@dataclass(frozen=True)
class State(ABC):
    """
    Abstract class to represent the state of an algorithm.
    """
    pid: Pid
    
    def cloned_with(self, **kwargs: dict[str, Any]) -> Self:
        """Create a copy of this state with updated attributes.
        
        Args:
            **kwargs: Attribute name-value pairs to update in the cloned state.
        
        Returns:
            A new State instance with the specified attributes updated.
        """
        return self.__class__(**{**self.__dict__, **kwargs})
    
    def as_str(self, keys: Optional[Iterable[str]] = None) -> str:
        """Get a formatted string representation of the state.
        
        Args:
            keys: An optional list of attribute keys to include in the string.
                  If None, all attributes are included except 'pid'.
        
        Returns:
            A formatted string representation showing pid and selected attributes.
        """
        keys = self.__dict__.keys() if keys is None else keys
        return f"{self.pid}: " + ", ".join(f"{k}={self.__dict__.get(k)!s}" for k in keys if k != "pid")
    
    def __str__(self) -> str:
        """
        String representation of the state.
        """
        return self.as_str()

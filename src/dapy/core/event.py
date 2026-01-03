# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from abc import ABC
from dataclasses import dataclass
from typing import Self

from .pid import Pid


@dataclass(frozen=True)
class Event(ABC):
    """
    Abstract class to represent an event in the system.
    
    There are two direct subclasses of this class:
    
    - `Signal`: represents a signal event (an event that occurs at a single process).
    - `Message`: represents a message transmission (an event issued at some process
        and received at a different target process).
    
    This class is not designed to be instantiated directly, but rather
    by subclassing either one of the two subclasses.
    
    Attributes:
        target: Pid
            The process identifier (PID) of the process that the event targets.
    """
    target: Pid
    
    def __str__(self) -> str:
        """Return a string representation of the event.
        
        Returns:
            A formatted string showing the event type, target process,
            and any additional attributes.
        """
        other_attributes = ', '.join(f"{k}={v!s}" for k,v in self.__dict__.items() if k != 'target' and v is not None)
        if other_attributes:
            other_attributes = "; " + other_attributes
        return f"{self.__class__.__name__}(@{self.target}{other_attributes})"
    
    def __lt__(self, other: Self) -> bool:
        """Check if this event is less than another event.
        
        Events are compared by their target process identifier.
        
        Args:
            other: The event to compare with.
        
        Returns:
            True if this event's target is less than the other event's target.
        """
        if not isinstance(other, Event):
            return NotImplemented
        if self == other:
            return False
        return self.target < other.target
    
    def __gt__(self, other: Self) -> bool:
        """
        Compare two events.
        """
        if not isinstance(other, Event):
            return NotImplemented
        if self == other:
            return False
        return self.target > other.target
    
    def __cmp__(self, other: Self) -> int:
        """
        Compare two events.
        """
        if not isinstance(other, Event):
            return NotImplemented
        if self == other:
            return 0
        if self.target == other.target:
            return hash(self).__cmp__(hash(other))
        return -1 if self.target < other.target else 1
    

@dataclass(frozen=True)
class Signal(Event):
    """
    Class to represent a signal event.
    
    A signal is an event that occurs internally with respect to a process.
    A signal can also be generated externally (with respect to the algorithm)
    and is typically issued at some processes at the initialization of the system.
    
    Signals are defined by creating subclasses of this class.
    The subclass must be frozen (immutable) and can hold additional
    attributes that are relevant to the signal.
    
    A signal can hold additional information in its attributes, but it is not mandatory.
    Typically, for a given algorithm, it is possible (and encouraged) to define multiple
    signals, each with an explicit name that makes its purpose clear. This makes it easy
    to discriminate between different signals in the algorithm using structural pattern
    matching (`match` statement).
    
    Attributes:
        target: Pid
            The process identifier (PID) of the process that the signal targets.
    """

@dataclass(frozen=True)
class Message(Event):
    """
    Class to represent a send/receive event.
    
    A message is an event that occurs between two processes.
    The sender and the receiver (target) are both specified.
    
    Messages are defined by creating subclasses of this class.
    The subclass must be frozen (immutable) and can hold additional
    attributes that are relevant to the message.
    
    Attributes:
        target: Pid
            The process identifier (PID) of the process that __receives__ the message (i.e, that the message targets).
        sender: Pid
            The process identifier (PID) of the process that __sends__ the message.
    """
    sender: Pid

from abc import ABC
from dataclasses import dataclass, field

from .pid import Pid


@dataclass(frozen=True, order=True)
class Event(ABC):
    """
    Abstract class to represent an event in the system.
    
    Attributes:
        target: Pid
            The process identifier (PID) of the process that the event targets.
    """
    target: Pid
    
    def __str__(self) -> str:
        """
        String representation of the start signal.
        """
        other_attributes = ', '.join(f"{k}={str(v)}" for k,v in self.__dict__.items() if k != 'target' and v is not None)
        if other_attributes:
            other_attributes = "; " + other_attributes
        return f"{self.__class__.__name__}(@{self.target}{other_attributes})"
        

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

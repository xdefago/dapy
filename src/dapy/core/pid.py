from dataclasses import dataclass, field
from typing import Iterable, Iterator, Self


@dataclass(frozen=True, order=True)
class Pid:
    """Represents a unique process identifier in a distributed system.
    
    Attributes:
        id: The unique numeric identifier for the process.
    """
    id: int
    
    def __str__(self) -> str:
        return f"p{self.id}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"


@dataclass(frozen=True)
class ProcessSet:
    """Represents an immutable set of process identifiers.
    
    Attributes:
        processes: A frozenset of unique process identifiers.
    """
    processes: frozenset[Pid] = field(default_factory=frozenset)
    
    def __init__(self, processes: Iterable[Pid] | Pid = frozenset()) -> None:
        if isinstance(processes, Pid):
            processes = {processes}
        object.__setattr__(self, 'processes', frozenset(processes))
        
    def __str__(self) -> str:
        return f"{{{','.join(str(p) for p in sorted(self.processes))}}}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({{{','.join(repr(p) for p in sorted(self.processes))}}})"
    
    def __contains__(self, pid: Pid) -> bool:
        return pid in self.processes
    
    def __len__(self) -> int:
        return len(self.processes)
    
    def __iter__(self) -> Iterator[Pid]:
        return iter(self.processes)
    
    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, ProcessSet):
            return False
        return self.processes == other.processes
    
    def __add__(self, other: Self | Pid | Iterable[Pid]) -> Self:
        if isinstance(other, Pid):
            return ProcessSet(processes=self.processes.union({other}))
        elif isinstance(other, ProcessSet):
            return ProcessSet(processes=self.processes.union(other.processes))
        elif isinstance(other, Iterable):
            return ProcessSet(processes=self.processes.union(other))
        else:
            raise TypeError("Cannot join ProcessSet with non-ProcessSet object")
        
    @staticmethod
    def empty() -> Self:
        """Create an empty process set.
        
        Returns:
            An empty ProcessSet instance.
        """
        return ProcessSet()


@dataclass(frozen=True, order=True)
class Channel:
    """Represents a communication channel between two processes.
    
    Channels can be directed (sender to receiver) or undirected.
    For undirected channels, the order of processes is normalized for equality.
    
    Attributes:
        s: The sender process identifier.
        r: The receiver process identifier.
        directed: Indicates if the channel is directed. Defaults to True.
    """
    s: Pid
    r: Pid
    directed: bool = True
    
    def __str__(self) -> str:
        return f"<{self.s.id},{self.r.id}>"
    
    def __repr__(self) -> str:
        if self.directed:
            return f"{self.__class__.__name__}({self.s!r},{self.r!r})"
        return f"{self.__class__.__name__}({self.s!r},{self.r!r}, directed=False)"

    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Channel):
            return False
        if self.directed and other.directed:
            return self.as_tuple() == other.as_tuple()
        else:
            return self.normalized() == other.normalized()
        
    def __cmp__(self, other: Self) -> int:
        if not isinstance(other, Channel):
            raise TypeError("Cannot compare Channel with non-Channel object")
        if self.directed and other.directed:
            a = self.as_tuple()
            b = other.as_tuple()
        else:
            a = self.normalized()
            b = other.normalized()
        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0
        
    def __hash__(self) -> int:
        if self.directed:
            return hash(self.as_tuple())
        else:
            return hash(self.normalized())
    
    def as_tuple(self) -> tuple[Pid, Pid]:
        """Convert the channel to a tuple of process identifiers.
        
        Returns:
            A tuple (sender, receiver) representing the channel.
        """
        return (self.s, self.r)
        
    def normalized(self) -> tuple[Pid, Pid]:
        """Return a normalized representation of the channel for comparison.
        
        For undirected channels, ensures the smaller PID comes first.
        
        Returns:
            A tuple where the first PID is always less than or equal to the second.
        """
        if self.s <= self.r:
            return (self.s, self.r)
        else:
            return (self.r, self.s)


@dataclass(frozen=True)
class ChannelSet:
    """Represents an immutable set of communication channels.
    
    Attributes:
        channels: A frozenset of unique Channel objects.
    """
    channels: frozenset[Channel] = field(init=False)
    
    def __init__(self, channels: Iterable[Channel] | Channel = frozenset()) -> None:
        if isinstance(channels, Channel):
            channels = {channels}
        object.__setattr__(self, 'channels', frozenset(channels))
        
    def __str__(self) -> str:
        return f"{{{','.join(str(c) for c in sorted(self.channels))}}}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({{{','.join(repr(c) for c in sorted(self.channels))}}})"
    
    def __contains__(self, channel: Channel) -> bool:
        return channel in self.channels
    
    def __len__(self) -> int:
        return len(self.channels)
    
    def __iter__(self) -> Iterator[Channel]:
        return iter(self.channels)
    
    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, ChannelSet):
            return False
        return self.channels == other.channels
    
    def __add__(self, other: Self | Channel | Iterable[Channel]) -> Self:
        if isinstance(other, Channel):
            return ChannelSet(channels=self.channels.union({other}))
        elif isinstance(other, ChannelSet):
            return ChannelSet(channels=self.channels.union(other.channels))
        elif isinstance(other, Iterable):
            return ChannelSet(channels=self.channels.union(other))
        else:
            raise TypeError("Cannot join ChannelSet with non-ChannelSet object")


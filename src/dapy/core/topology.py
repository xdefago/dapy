from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator, Self

from .pid import Channel, Pid, ProcessSet


@dataclass(frozen=True)
class NetworkTopology(ABC):
    """
    Abstract class to represent a network topology.
    """
    @abstractmethod
    def neighbors_of(self, pid: Pid) -> ProcessSet:
        """Get the neighbors of the given process in the topology.
        
        Args:
            pid: The process identifier.
        
        Returns:
            A ProcessSet containing all neighbors of the given process.
        """
        pass
    
    @abstractmethod
    def processes(self) -> ProcessSet:
        """Return the set of all processes in the topology.
        
        Returns:
            A ProcessSet containing all processes in this topology.
        """
        pass
    
    def __len__(self) -> int:
        # default implementation; expected to be overridden in subclasses
        # for the sake of performance
        return len(self.processes())

    def __contains__(self, pid: Pid) -> bool:
        # default implementation; expected to be overridden in subclasses
        # for the sake of performance
        return pid in self.processes()
    
    def __iter__(self) -> Iterator[Pid]:
        # default implementation; expected to be overridden in subclasses
        # for the sake of performance
        return iter(self.processes())
    


@dataclass(frozen=True)
class CompleteGraph(NetworkTopology):
    _processes: frozenset[Pid]
    
    def neighbors_of(self, pid: Pid) -> ProcessSet:
        return ProcessSet(self._processes - {pid})

    def processes(self) -> ProcessSet:
        return ProcessSet(self._processes)
    
    def __len__(self) -> int:
        return len(self._processes)
    def __contains__(self, pid: Pid) -> bool:
        return pid in self._processes
    def __iter__(self) -> Iterator[Pid]:
        return iter(self._processes)

    @classmethod
    def from_(cls, processes: Iterable[Pid]) -> Self:
        return cls(frozenset(processes))
    
    @classmethod
    def of_size(cls, size: int) -> Self:
        """Create a complete graph topology with the given number of processes.
        
        In a complete graph, every process is connected to every other process.
        
        Args:
            size: The number of processes in the topology. Must be positive.
        
        Returns:
            A CompleteGraph instance with sequential process IDs from 1 to size.
        
        Raises:
            ValueError: If size is not a positive integer.
        """
        if size <= 0:
            raise ValueError("Size must be a positive integer.")
        return cls.from_(Pid(i+1) for i in range(size))


@dataclass(frozen=True)
class Ring(NetworkTopology):
    _processes: list[Pid] = field()
    _index: dict[Pid, int] = field()
    directed: bool = field(default=False)
    
    def neighbors_of(self, pid: Pid) -> ProcessSet:
        idx = self._index.get(pid)
        if idx is None:
            raise ValueError(f"Process {pid} not found in the ring topology.")
        if self.directed:
            return frozenset({self._processes[(idx + 1) % len(self._processes)]})
        return ProcessSet({self._processes[(idx - 1)], 
                          self._processes[(idx + 1) % len(self._processes)]})

    def processes(self) -> ProcessSet:
        return ProcessSet(self._processes)

    def __len__(self) -> int:
        return len(self._processes)
    def __contains__(self, pid: Pid) -> bool:
        return pid in self._processes
    def __iter__(self) -> Iterator[Pid]:
        return iter(self._processes)
        
    @classmethod
    def from_(cls, processes: Iterable[Pid], directed: bool = False) -> Self:
        processes = sorted(set(processes))
        index = {pid: i for i, pid in enumerate(processes)}
        return cls(processes, index, directed)
    
    @classmethod
    def of_size(cls, size: int, directed: bool = False) -> Self:
        """
        Create a ring topology with the given size.
        """
        if size <= 0:
            raise ValueError("Size must be a positive integer.")
        return cls.from_((Pid(i+1) for i in range(size)), directed=directed)


@dataclass(frozen=True)
class Star(NetworkTopology):
    _center: Pid
    _leaves: frozenset[Pid]
    
    def __post_init__(self) -> None:
        if len(self._leaves) < 1:
            raise ValueError("A star topology must have at least one leaf.")
        if self._center in self._leaves:
            raise ValueError("Center cannot be a leaf.")
        
    def center(self) -> Pid:
        return self._center
    
    def neighbors_of(self, pid: Pid) -> ProcessSet:
        if pid == self._center:
            return ProcessSet(self._leaves)
        if pid in self._leaves:
            return ProcessSet(self._center)
        raise ValueError(f"Process {pid} not found in the star topology.")

    def processes(self) -> ProcessSet:
        return ProcessSet({self._center} | self._leaves)

    def __len__(self) -> int:
        return 1 + len(self._leaves)
    def __contains__(self, pid: Pid) -> bool:
        return pid == self._center or pid in self._leaves
    def __iter__(self) -> Iterator[Pid]:
        return iter({self._center} | self._leaves)
        
    @classmethod
    def from_(cls, center: Pid, leaves: Iterable[Pid]) -> Self:
        leaves = frozenset(leaves)
        return cls(center, leaves)
    
    @classmethod
    def of_size(cls, size: int) -> Self:
        """
        Create a star topology with the given size.
        """
        if size <= 1:
            raise ValueError("Size must be greater than 1.")
        center = Pid(1)
        leaves = (Pid(i+2) for i in range(size - 1))
        return cls.from_(center, leaves)


@dataclass(frozen=True)
class Arbitrary(NetworkTopology):
    _neighbors: dict[Pid, ProcessSet]
    _processes: ProcessSet = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(self, '_processes', ProcessSet(self._neighbors.keys()))
        
    def neighbors_of(self, pid: Pid) -> ProcessSet:
        return self._neighbors.get(pid, ProcessSet())
    
    def processes(self) -> ProcessSet:
        return self._processes
    
    @classmethod
    def from_(cls,
              channels: Iterable[Pid | tuple[Pid, Pid] | Channel | tuple[int, int]],
              directed: bool = True
    ) -> Self:
        neighbors: dict[Pid, ProcessSet] = {}
        for entry in channels:
            if isinstance(entry, Pid):
                neighbors.setdefault(entry, ProcessSet())
            else:
                if isinstance(entry, Channel):
                    s, r = entry.as_tuple()
                elif isinstance(entry, tuple) and isinstance(entry[0], int) and isinstance(entry[1], int):
                    s, r = Pid(entry[0]), Pid(entry[1])
                else:
                    s, r = entry
                neighbors.setdefault(s, ProcessSet())
                neighbors[s] = neighbors[s] + r
                if not directed:
                    neighbors.setdefault(r, ProcessSet())
                    neighbors[r] = neighbors[r] + s
                    
        return cls(neighbors)

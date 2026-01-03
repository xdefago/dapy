"""
This module implements the "Learn the Topology" algorithm, from the .
"""

from dataclasses import dataclass, field
from typing import Sequence

from ..core import Algorithm, Channel, ChannelSet, Event, Message, Pid, ProcessSet, Signal, State


#
# Messages and signals used in the algorithm.
#
@dataclass(frozen=True)
class PositionMsg(Message):
    """Message containing topology information from a process.
    
    Used to propagate knowledge of the network topology during the
    learn topology algorithm.
    
    Attributes:
        origin: The identifier of the process whose neighbors are being shared.
        neighbors: The set of neighbor processes of the origin process.
    """
    origin: Pid
    neighbors: ProcessSet = field(default_factory=ProcessSet)

@dataclass(frozen=True)
class Start(Signal):
    """Signal to initiate the topology learning algorithm in a process."""

@dataclass(frozen=True)
class GraphIsKnown(Signal):
    """Signal indicating that a process has learned the complete network topology."""
    pass



#
# State of a process in the algorithm.
#
@dataclass(frozen=True)
class LearnState(State):
    """State maintained by a process during the topology learning algorithm.
    
    Attributes:
        neighbors_i: The set of neighbor processes (constant throughout execution).
        proc_known_i: The set of processes whose existence this process has learned.
        channels_known_i: The set of communication channels (directed edges) learned.
        part_i: Boolean flag indicating if this process has started (participated).
    """
    neighbors_i: ProcessSet = field(default_factory=ProcessSet)
    proc_known_i: ProcessSet = field(default_factory=ProcessSet)
    channels_known_i: ChannelSet = field(default_factory=ChannelSet)
    part_i: bool = False



#
# The algorithm itself.
# 
@dataclass(frozen=True)
class LearnGraphAlgorithm(Algorithm[LearnState]):
    """Algorithm for distributed learning of the network topology.
    
    This algorithm enables each process to learn the complete network topology
    by having processes exchange their known neighbors. Each process initiates
    by sending its neighbors to all neighbors, then forwards received information
    to remaining neighbors until the complete graph is known.
    
    Attributes:
        is_verbose: Enable verbose output of algorithm events. Defaults to False.
    """
    is_verbose: bool = False
    
    @property
    def name(self) -> str:
        """Get the name of the algorithm.
        
        Returns:
            The string "Learn the Topology".
        """
        return "Learn the Topology"
    
    #
    # Mandatory method: given a process id, create and return the initial state of that process.
    #
    def initial_state(self, pid: Pid) -> LearnState:
        """Create the initial state for a process.
        
        Args:
            pid: The process identifier.
        
        Returns:
            A LearnState initialized with the process's neighbors from the topology.
        """
        return LearnState(
            pid=pid,
            neighbors_i=self.system.topology.neighbors_of(pid),
            part_i=False,
        )
    
    #
    # Mandatory method:
    # given the state of a process and an event (signal or message) applied to it,
    # return the new state of the process and a list of events to be scheduled.
    #
    def on_event(self, old_state: LearnState, event: Event) -> tuple[LearnState, Sequence[Event]]:
        """Process an event and update the process state.
        
        Handles Start signals to initiate the algorithm, PositionMsg messages
        to learn about other processes and channels, and GraphIsKnown signals.
        
        Args:
            old_state: The current state of the process.
            event: The event to process (Start, PositionMsg, or GraphIsKnown).
        
        Returns:
            A tuple of (new_state, list_of_new_events) to send.
        
        Raises:
            NotImplementedError: If an unknown event type is received.
        """
        
        match event:
            
            # () when Start() is received do
            # (5)     if (not part_i) then start() end if            
            case Start(_):
                if not old_state.part_i:
                    return self._do_start(old_state)
                else:
                    # do nothing
                    return old_state, []
                
            # () when Position(id, neighbors) is received from neighbor id_x do
            case PositionMsg(_, id_x, id, neighbors):
                new_state = old_state
                new_events: list[Event] = []
                # (6) if (not part_i) then start() end if
                if not new_state.part_i:
                    new_state, events_from_start = self._do_start(new_state)
                    new_events = list(events_from_start)

                # (7) if id not in proc_known_i then                    
                if id not in new_state.proc_known_i:
                    # (8) proc_known_i := proc_known_i ∪ {id}
                    # (9) channels_known_i := channel_known_i ∪ {<id, id_k> | id_k in neighbors>}
                    # add the new position to the state
                    new_state = new_state.cloned_with(
                        proc_known_i=new_state.proc_known_i + id,
                        channels_known_i=new_state.channels_known_i +
                            ChannelSet( Channel(id, neighbor) for neighbor in neighbors ),
                    )
                    # (10) for each id_y in neighbors_i \ {id_x} do
                    # (11)  send POSITION(id, neighbors) to id_y
                    # (12) end for
                    # send the position to all neighbors except the sender
                    new_events = new_events + [
                        PositionMsg(target=neighbor, sender=old_state.pid, origin=id, neighbors=neighbors)
                        for neighbor in old_state.neighbors_i
                        if neighbor != id_x
                    ]
                    # (13) if forall<id_j, id_k> in channels_known_i : {id_j, id_k} in proc_known_i) then
                    # (14)    p_i knowns the communication graph
                    # (15) end if
                    if all(
                        c_jk.r in new_state.proc_known_i and c_jk.s in new_state.proc_known_i
                        for c_jk in new_state.channels_known_i
                    ):
                        new_events.append(GraphIsKnown(target=new_state.pid))
                    
                # return the new states and all send events
                return new_state, new_events
            
            case GraphIsKnown(_):
                # Handle the graph known event
                if self.is_verbose:
                    print(f"Graph is known for {old_state.pid}")
                return old_state, []
            
            case _:
                # Handle other events
                raise NotImplementedError(f"Event {event} not implemented in {self.name}")
            
    #
    # Custom method defined for modularity.
    # Corresponds to the start() method in the pseudo-code of the algorithm.
    #
    # () operation start() is
    # (1)    for each id_j in neighbors_i do
    # (2)        send POSITION(id, neighbors) to id_j
    # (3)    end for
    # (4)    part_i <- true
    # (5) end operation
    def _do_start(self, state: LearnState) -> tuple[LearnState, Sequence[Event]]:
        """Initialize the topology learning process.
        
        Sends the process's initial neighbors to all neighbors and marks
        the process as participating in the algorithm.
        
        Args:
            state: The current state of the process.
        
        Returns:
            A tuple of (updated_state, list_of_position_messages) to send.
        """
        events = [
            PositionMsg(target=neighbor, sender=state.pid, origin=state.pid, neighbors=state.neighbors_i)
            for neighbor in state.neighbors_i
        ]
        state = state.cloned_with(
            proc_known_i=ProcessSet(state.pid),
            channels_known_i=ChannelSet( Channel(state.pid, neighbor) for neighbor in state.neighbors_i ),
            part_i=True, # part_i <- true
        )
        return state, events


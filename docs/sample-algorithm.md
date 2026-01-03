# Example (Part 1)

* How to write an algorithm
* [How to define an execution](sample-execution.md)

## How to write an algorithm

Writing an algorithm in this framework requires the definition of three kinds of elements:
* process state (subclass of `State`)
* messages and signal types (subclasses of `Message` or `Signal`)
* the algorithm code (subclass of `Algorithm`)

For instance, consider the "Learn the Topology" algorithm defined in [`learn.py`](src/dapy/algo/learn.py) and see how these three elements are declared.

### State

The state is defined as follows (simplified version):
```python
from dataclasses import dataclass, field
from dapy.core import State, ProcessSet, ChannelSet

#
# State of a process in the algorithm.
#
@dataclass(frozen=True)
class LearnState(State):
    neighbors_i: ProcessSet = field(default_factory=ProcessSet)
    proc_known_i: ProcessSet = field(default_factory=ProcessSet)
    channels_known_i: ChannelSet = field(default_factory=ChannelSet)
    part_i: bool = False
```

This describes the information held by a process at a given point in time. The class `LearnState` is specific for the Learn algorithm and must be declared as a subclass of the class `State`. The subclass must be a `dataclass` and declared to be immutable (`frozen=True`), which means that the information will never change after an new instance is created.
Every instance that derives from `State` inherits a field `pid` of type `Pid` defined in the superclass. This represents the identifier of the process for which it is instantiated.


### Messages and signals

The algorithm will react to messages (sent by one process to be received by another) and signals (event affecting a single process locally).
Collectively, both `Message` and `Signal` derive from a superclass `Event`.

All events have a field `target` of type `Pid`. This indicates which process the event targets (i.e., which process will handle that event). In the case of a message, this is the destination process.

All messages have additionally a field `sender` of `Pid`. This indicates which process has sent the message.

Concretely, the learn algorithm uses `PositionMsg` as message between processes and `Start` as local event. In addition, this code declares a new signal `GraphIsKnown`, not found in the pseudo-code, to be issued at a process when that process has learned the entire graph.

```python
from dataclasses import dataclass, field
from dapy.core import Pid, ProcessSet, Message, Signal

#
# Messages and signals used in the algorithm.
#
@dataclass(frozen=True)
class PositionMsg(Message):
    origin: Pid
    neighbors: ProcessSet = field(default_factory=ProcessSet)

@dataclass(frozen=True)
class Start(Signal):
    pass

@dataclass(frozen=True)
class GraphIsKnown(Signal):
    pass
```

### Algorithm

With the main ingredients defined (state and messages), this leaves the writing of the algorithm itself.
This is done by defining a subclass of `Algorithm` with at least two methods defined:
* `initial_state(self, pid) -> State:`<br>
    Given a process identifier `pid`, constructs the initial state for that algorithm.
* `on_event(self, old_state: State, event: Event) -> tuple[State, list[Event]]:`<br>
    Given a state and an event, compute a new state and generate a list of events (messages or signals) to be scheduled later.
    Note that the state is immutable. However, one can create a derived and modified instance of a state, using the method `clone_with` and named parameters. See the example below.

The base class `Algorithm` defines a field `system` that holds information about the system (or at least where a process can find the information that is implicitly known, such as its neighbors).

The base class defines a property function `name` that can be optionally overridden to give a name to the algorithm (the class name is used by default).

The base class defines also a function `on_start` that can be optionally overridden to be called with the initial state and that can optionally issue some events initially. By default, the method does nothing.

To get back to the concrete example of Learn the Topology algorithm, 

```python
from dataclasses import dataclass
from dapy.core import ProcessSet, Event, Pid
from dapy.core import ProcessSet, ChannelSet, Channel
from dapy.core import Algorithm

#
# The algorithm itself.
# 
@dataclass(frozen=True)
class LearnGraphAlgorithm(Algorithm):
    """
    This algorithm learns the topology of the network.
    """
    
    @property
    def name(self) -> str:
        """
        Return the name of the algorithm.
        """
        return "Learn the Topology"
    
    #
    # Mandatory method: given a process id, create and return the initial state of that process.
    #
    def initial_state(self, pid: Pid) -> LearnState:
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
    def on_event(self, old_state: LearnState, event: Event) -> tuple[LearnState, list[Event]]:

        match event:
            
            # () when Start() is received do
            # (5)     if (not part_i) then start() end if            
            case Start(_) if not old_state.part_i:
                if not old_state.part_i:
                    return self._do_start(old_state)
                else:
                    # do nothing
                    return old_state, []
                
            # () when Position(id, neighbors) is received from neighbor id_x do
            case PositionMsg(_, id_x, id, neighbors):
                new_state = old_state
                new_events = []
                # (6) if (not part_i) then start() end if
                if not new_state.part_i:
                    new_state, new_events = self._do_start(new_state)

                # (7) if id not in proc_known_i then                    
                if id not in new_state.proc_known_i:
                    # (8) proc_known_i := proc_known_i ∪ {id}
                    # (9) channels_known_i := channel_known_i ∪ {<id, id_k> | id_k in neighbors>}
                    # add the new position to the state
                    new_state = new_state.cloned_with(
                        proc_known_i=new_state.proc_known_i + id,
                        channels_known_i=(
                            new_state.channels_known_i
                            + ChannelSet(
                                Channel(id, neighbor) for neighbor in neighbors
                            )
                        ),
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
    def _do_start(self, state: LearnState) -> tuple[LearnState, list[Event]]:
        """
        Handle the start of the algorithm.
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
```

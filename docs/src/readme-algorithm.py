# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Sequence

from dapy.algo.learn import GraphIsKnown, LearnState, PositionMsg, Start
from dapy.core import Algorithm, Channel, ChannelSet, Event, Pid, ProcessSet


#
# The algorithm itself.
# 
@dataclass(frozen=True)
class LearnGraphAlgorithm(Algorithm[LearnState]):
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
    def on_event(self, old_state: LearnState, event: Event) -> tuple[LearnState, Sequence[Event]]:
        
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
    def _do_start(self, state: LearnState) -> tuple[LearnState, Sequence[Event]]:
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

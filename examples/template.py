# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from typing import Sequence

from dapy.core import Algorithm, Event, Message, Pid, Signal, State

#
# Define the State of a process in the algorithm.
#

@dataclass(frozen=True)
class MyState(State):
    # inherited from State
    #   pid: Pid
    # declare any other relevant fields
    ...

#
# Define the messages and signals used in the algorithm.
#

@dataclass(frozen=True)
class MyMessage(Message):
    # inherited from Message
    #   target: Pid
    #   sender: Pid
    # declare any other relevant fields
    ...
    
@dataclass(frozen=True)
class MySignal(Signal):
    # inherited from Signal
    #   target: Pid
    # declare any other relevant fields
    ...
    
#
# Define the algorithm itself.
#
@dataclass(frozen=True)
class MyAlgorithm(Algorithm[MyState]):
    """Brief description of what this algorithm does.
    
    The description is automatically extracted from this docstring.
    """
    # inherited from Algorithm
    #   system: System
    
    # Optional class variables for metadata (appear in traces and viewer)
    # algorithm_name: Optional[str] = "My Algorithm"  # defaults to class name if not set
    # algorithm_description: Optional[str] = None  # defaults to the description in docstring if not set
    
    #
    # Mandatory method: given a process id, create and return the initial state of that process.
    #
    def initial_state(self, pid: Pid) -> MyState:
        """
        Create and return the initial state of the process.
        """
        return MyState(
            pid=pid,
            # initialize any other relevant fields
            # ...
        )
    
    #
    # Mandatory method:
    # given the state of a process and an event (signal or message) applied to it,
    # return the new state of the process and a list of events to be scheduled.
    #
    def on_event(self, old_state: MyState, event: Event) -> tuple[MyState, Sequence[Event]]:
        """
        Given the state of a process and an event, return the new state and a list of events to be scheduled.
        """
        # implement the algorithm logic here
        ...
        new_state = old_state.cloned_with(...)  # create the new state
        new_events: list[Event] = [...]  # create any events to be scheduled
        ...
        return new_state, new_events

    #
    # Optional methods
    #
    
    def on_start(self, init_state: MyState) -> tuple[MyState, Sequence[Event]]:
        """Given the initial state of a process, return a modified state and a sequence of events to be scheduled.
        """
        # Although the the state can be modified, the intention is mainly to provide a way to issue initial events.
        # This is not always needed, as the initial events can also be scheduled externally.
        return init_state, [...]  # possibly schedule some initial events



if __name__ == "__main__":
    #
    # Algorithm execution
    #

    from dapy.core import System  # ...
    from dapy.sim import Settings, Simulator

    #
    # optionally define settings (e.g. enable trace)
    #
    settings = Settings(enable_trace=True)

    #
    # define the system (topology, synchrony model)
    #
    system = System(
        topology= ...,  # e.g., RingTopology(num_processes=5)
        synchrony= ..., # e.g., SynchronousModel()
    )

    #
    # Instantiate the algorithm
    #
    algorithm = MyAlgorithm(system)

    #
    # Create the simulator environment
    #
    sim = Simulator.from_system(system, algorithm, settings=settings)

    #
    # Run the simulation
    #
    
    # Start the simulation; all processes are initialized to their initial state 
    sim.start()
    # Possibly schedule some initial event(s)
    sim.schedule(event=..., at=...)  # e.g., sim.schedule(event=MySignal(target=Pid(1)), at=simtime(seconds=0))
    # Run the algorithm until completion
    sim.run_to_completion()

    #
    # Check the final state of the system
    #
    print(sim.current_time) # final time reached by the simulation
    print(sim.current_configuration) # final configuration of the system
    print(sim.trace) # trace of the simulation (if enabled)

# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

import heapq

from dataclasses import dataclass, field
from typing import Optional, Self

from ..core import Algorithm, Event, Message, System, SimTime, simtime
from .configuration import Configuration
from .settings import Settings
from .timed import TimedEvent
from .trace import Trace


@dataclass
class Simulator:
    """Simulates the execution of a distributed algorithm on a system.
    
    The simulator manages the execution of a distributed algorithm by processing
    events (messages and signals) in chronological order on a system with a
    specific synchrony model.
    
    Attributes:
        system: The distributed system to simulate (topology and synchrony model).
        algorithm: The distributed algorithm to execute.
        current_configuration: The current state of all processes.
        current_time: The current simulation time. Defaults to 0 seconds.
        settings: Configuration settings for the simulation. Defaults to default Settings.
        trace: Optional trace object for recording simulation events.
        scheduled_events: Priority queue of events waiting to be processed.
    """
    system: System
    algorithm: Algorithm
    current_configuration: Configuration
    current_time: SimTime = field(default=simtime())
    settings: Settings = field(default_factory=Settings)
    trace: Optional[Trace] = field(default=None)
    scheduled_events: list[TimedEvent] = field(default_factory=list, init=False)
    
    
    def __post_init__(self) -> None:
        """Initialize the simulator with the given settings.
        
        Sets up tracing if enabled in the settings.
        """
        if self.settings.enable_trace:
            # Extract synchrony model information
            sync_model = self.system.synchrony
            sync_name = type(sync_model).__name__
            sync_params = {}
            
            # Extract parameters based on synchrony model type
            if hasattr(sync_model, 'fixed_delay'):
                sync_params['fixed_delay'] = str(sync_model.__getattribute__('fixed_delay'))
            if hasattr(sync_model, 'max_delay'):
                sync_params['max_delay'] = str(sync_model.__getattribute__('max_delay'))
            if hasattr(sync_model, 'delta_t'):
                sync_params['delta_t'] = str(sync_model.__getattribute__('delta_t'))
            sync_params['min_delay'] = sync_model.min_delay
            
            self.trace = Trace(
                system=self.system,
                algorithm_name=self.algorithm.name,
                algorithm_description=self.algorithm.description,
                synchrony_model_name=sync_name,
                synchrony_model_params=sync_params,
                trace_format_version="1.0"
            )
    
    @classmethod
    def from_system(cls,
                    system: System,
                    algorithm: Algorithm,
                    starting_time: SimTime = simtime(),
                    settings: Settings = Settings()
    ) -> Self:
        """Create a simulator instance from a system and algorithm.
        
        Args:
            system: The distributed system to simulate.
            algorithm: The distributed algorithm to execute.
            starting_time: The initial simulation time. Defaults to 0 seconds.
            settings: Configuration settings for the simulation.
                     Defaults to default Settings.
        
        Returns:
            A new Simulator instance initialized with the given system and algorithm.
        """
        current_configuration = Configuration.from_states( algorithm.initial_state(p) for p in system.processes())
        return cls(
            system=system,
            algorithm=algorithm,
            current_configuration=current_configuration,
            current_time=starting_time,
            settings=settings
        )       
    
    def start(self) -> None:
        """Initialize and start the simulation.
        
        Resets the simulation time to 0 and invokes the algorithm's on_start
        handler for each process to generate initial events.
        """
        self.current_time = simtime()
        for pid in self.system.processes():
            initial_state, events = self.algorithm.on_start(self.current_configuration[pid])
            self.current_configuration = self.current_configuration.updated([initial_state])
            for event in events:
                at_time = self._arrival_time_for(event)
                self.schedule(event, at_time)
    
    def _arrival_time_for(self, event: Event) -> SimTime:
        """Calculate the arrival time for a given event based on the synchrony model.
        
        Args:
            event: The event to calculate arrival time for.
        
        Returns:
            The time when the event should be delivered according to the
            system's synchrony model.
        """
        if isinstance(event, Message):
            return self.system.synchrony.arrival_time_for(self.current_time)
        else:
            return self.current_time
        
    def schedule(self, event: Event, at: SimTime = simtime()) -> None:
        """Schedule an event to be processed at a specific time.
        
        Args:
            at: The time when the event should be processed.
            event: The event to schedule.
        """
        time = max(self.current_time, at)
        heapq.heappush(self.scheduled_events, TimedEvent(time=time, event=event))
        if self.trace is not None:
            self.trace.add_events([(self.current_time, time, event)])

    def _apply_event(self, event: Event) -> None:
        """Apply an event to the current configuration.
        
        Updates the target process's state and schedules any new events
        generated by the algorithm's event handler.
        
        Args:
            event: The event to apply to the system.
        
        Raises:
            ValueError: If the target process is not in the current configuration.
        """
        pid = event.target
        if pid not in self.current_configuration:
            raise ValueError(f"{pid} not found in the current configuration.")
        old_state = self.current_configuration[pid]
        new_state, new_events = self.algorithm.on_event(old_state, event)
        self.current_configuration = self.current_configuration.updated([new_state])
        for new_event in new_events:
            at_time = self._arrival_time_for(new_event)
            self.schedule(new_event, at_time)
        
    def advance_step(self) -> None:
        """Advance the simulation by processing one scheduled event.
        
        Pops the earliest scheduled event from the priority queue and applies
        it to the current configuration, updating the simulation time.
        """
        if len(self.scheduled_events) > 0:
            next_event = heapq.heappop(self.scheduled_events)
            self.current_time = max(self.current_time, next_event.time)
            self._apply_event(next_event.event)
            if self.trace is not None:
                self.trace.add_history([(self.current_time, self.current_configuration)])

    def run_to_completion(self, step_limit: Optional[int] = None) -> None:
        """Run the simulation until completion or until a step limit is reached.
        
        Args:
            step_limit: Maximum number of steps to execute. If None, runs until
                       no more events are scheduled. Defaults to None.
        """
        step_count = 0
        while not self.is_finished() and (step_limit is None or step_count < step_limit):
            self.advance_step()
            step_count += 1

    def is_finished(self) -> bool:
        """Check if the simulation has finished.
        
        Returns:
            True if there are no more scheduled events, False otherwise.
        """
        return len(self.scheduled_events) == 0

    def save_trace(self, filename: str, format: str = 'pickle') -> None:
        """Save the simulation trace to a file.
        
        Convenience method to save trace without manually calling dump methods.
        Automatically determines binary vs text mode based on format.
        
        Args:
            filename: Path to the output file. Extension is not enforced but
                     .pkl recommended for pickle, .json for JSON.
            format: Serialization format - 'pickle' (default, compact and fast)
                   or 'json' (human-readable, requires dapy[json]).
        
        Raises:
            ValueError: If trace is not enabled or format is invalid.
            ImportError: If JSON format is requested but classifiedjson not installed.
        """
        if self.trace is None:
            raise ValueError(
                "No trace available. Enable tracing by setting enable_trace=True "
                "in Settings when creating the simulator."
            )
        
        from pathlib import Path
        path = Path(filename)
        
        if format == 'pickle':
            # Binary mode for pickle
            with open(path, 'wb') as f:
                f.write(self.trace.dump_pickle())
        elif format == 'json':
            # Text mode for JSON
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.trace.dump_json())
        else:
            raise ValueError(f"Invalid format '{format}'. Use 'pickle' or 'json'.")

    def __str__(self) -> str:
        """Get a string representation of the simulator state.
        
        Returns:
            A formatted string showing the current configuration, time,
            algorithm name, and scheduled events.
        """
        scheduled = '\n'.join( f"  {timed_event.time}: {timed_event.event}" for timed_event in self.scheduled_events )
        return f"""Simulator ({self.algorithm.name}) @{self.current_time}:
{self.current_configuration}
Scheduled Events:
{scheduled}"""

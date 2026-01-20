"""
Simulation runner for the broadcast algorithm

Run with: uv run run-bcast
Or: uv run python -m broadcast.run_bcast
"""

from datetime import timedelta
from pathlib import Path

from dapy.core import Asynchronous, Pid, Ring, System
from dapy.sim import Settings, Simulator

from .algo.algorithm import BroadcastAlgorithm, Start


def main() -> None:
    """Run the broadcast algorithm simulation."""
    
    # ========================================================================
    # 1. Create System Topology
    # ========================================================================
    
    # Create a ring of 5 processes
    # Other topologies: FullMesh, Star, Line, Tree, or custom NetworkTopology
    system = System(
        topology=Ring.of_size(5),
        synchrony=Asynchronous()  # Or Synchronous() for lockstep execution
    )
    
    print("=" * 60)
    print("Distributed Algorithm Simulation")
    print("=" * 60)
    print("Topology: Ring of 5 processes")
    print(f"Synchrony: {type(system.synchrony).__name__}")
    print()
    
    # ========================================================================
    # 2. Create Algorithm Instance
    # ========================================================================
    
    algorithm = BroadcastAlgorithm(system)
    print(f"Algorithm: {algorithm.name}")
    print()
    
    # ========================================================================
    # 3. Configure Simulation Settings
    # ========================================================================
    
    settings = Settings(
        enable_trace=True,  # Enable trace collection for visualization
    )
    
    # ========================================================================
    # 4. Create and Initialize Simulator
    # ========================================================================
    
    sim = Simulator.from_system(system, algorithm, settings=settings)
    sim.start()
    
    # ========================================================================
    # 5. Schedule Initial Events
    # ========================================================================
    
    # Process p0 initiates the broadcast
    initiator = Pid(0)
    initial_event = Start(target=initiator)
    
    print(f"Initiating broadcast from process {initiator}")
    sim.schedule(event=initial_event, at=timedelta(seconds=0))
    print()
    
    # ========================================================================
    # 6. Run Simulation
    # ========================================================================
    
    print("Running simulation...")
    sim.run_to_completion()
    print()
    
    # ========================================================================
    # 7. Save Trace for Visualization
    # ========================================================================
    
    # Create traces directory if it doesn't exist
    traces_dir = Path("traces")
    traces_dir.mkdir(exist_ok=True)
    
    trace_file = traces_dir / "broadcast_trace.pkl"
    
    # Save trace as pickle (default format - compact and fast)
    with open(trace_file, 'wb') as f:
        assert sim.trace is not None
        f.write(sim.trace.dump_pickle())
    
    print("=" * 60)
    print("Simulation Complete!")
    print("=" * 60)
    print(f"Trace saved to: {trace_file}")
    print()
    print("Visualize with:")
    print(f"  dapyview {trace_file}")
    print()
    
    # ========================================================================
    # 8. Optional: Print Statistics
    # ========================================================================
    
    print("Statistics:")
    print(f"  Total events in trace: {len(sim.trace.events_list)}")
    print(f"  Simulation time: {sim.current_time}")
    print()


if __name__ == "__main__":
    main()

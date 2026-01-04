# Copyright (c) 2025-2026 Xavier Defago
# SPDX-License-Identifier: MIT

"""
Simulation runner for your algorithm.

Run with: uv run run-my-algo
Or: uv run python -m my_algo.run_my_algo
"""


from dapy.core import System, Ring, Asynchronous
from dapy.sim import Settings

# Import your algorithm components
# Uncomment and modify after implementing your algorithm
# from .algorithm import MyAlgorithm, MySignal


def main():
    """Run your algorithm simulation."""
    
    # ========================================================================
    # 1. Create System Topology
    # ========================================================================
    
    # Define the network topology for your distributed system.
    # Common topologies:
    #   - Ring.of_size(n): Processes arranged in a ring
    #   - FullMesh.of_size(n): Every process connected to every other
    #   - Star.of_size(n): One central process connected to all others
    #   - Line.of_size(n): Processes in a linear chain
    #   - Tree.of_height(h): Binary tree of given height
    #   - Or create custom topology with NetworkTopology
    
    system = System(
        topology=Ring.of_size(5),  # Modify: Choose your topology
        synchrony=Asynchronous()   # Modify: Asynchronous() or Synchronous()
    )
    
    print("=" * 60)
    print("Distributed Algorithm Simulation")
    print("=" * 60)
    print(f"Topology: {type(system.topology).__name__} with {len(list(system.processes()))} processes")
    print(f"Synchrony: {type(system.synchrony).__name__}")
    print()
    
    # ========================================================================
    # 2. Create Algorithm Instance
    # ========================================================================
    
    # TODO: Uncomment and replace with your algorithm
    # algorithm = MyAlgorithm(system)
    # print(f"Algorithm: {algorithm.name}")
    # print()
    
    print("ERROR: Algorithm not implemented yet!")
    print("Please implement your algorithm in my_algo/algorithm.py")
    print("Then uncomment the algorithm instantiation above.")
    return
    
    # ========================================================================
    # 3. Configure Simulation Settings
    # ========================================================================
    
    # Settings control trace collection and other simulation behavior
    _ = Settings(
        enable_trace=True,  # Set to True to save execution trace for visualization
    )
    
    # ========================================================================
    # 4. Create and Initialize Simulator
    # ========================================================================
    
    # The simulator manages the execution of your algorithm
    # sim = Simulator.from_system(system, algorithm, settings=settings)
    # sim.start()
    
    # ========================================================================
    # 5. Schedule Initial Events
    # ========================================================================
    
    # Schedule any initial events to kick off the algorithm.
    # For example, if process 0 should start the protocol:
    # initiator = Pid(0)
    # sim.schedule_event(timedelta(seconds=0), MySignal(target=initiator))
    # print(f"Scheduled initial event for process {initiator}")
    # print()
    
    # ========================================================================
    # 6. Run Simulation
    # ========================================================================
    
    # Run the simulation until no more events are pending
    # print("Running simulation...")
    # sim.run_to_completion()
    # print()
    
    # ========================================================================
    # 7. Save Trace for Visualization
    # ========================================================================
    
    # Create traces directory if it doesn't exist
    # traces_dir = Path("traces")
    # traces_dir.mkdir(exist_ok=True)
    
    # Choose a descriptive filename for your trace
    # trace_file = traces_dir / "my_algorithm_trace.pkl"
    
    # Save trace (pickle format is default, smaller and faster)
    # with open(trace_file, 'wb') as f:
    #     assert sim.trace is not None
    #     f.write(sim.trace.dump_pickle())
    
    # Alternative: Save as JSON (larger file, human-readable)
    # trace_file_json = traces_dir / "my_algorithm_trace.json"
    # with open(trace_file_json, 'w') as f:
    #     f.write(sim.trace.dump_json())
    
    # print("=" * 60)
    # print("Simulation Complete!")
    # print("=" * 60)
    # print(f"Trace saved to: {trace_file}")
    # print()
    # print("Visualize with:")
    # print(f"  dapyview {trace_file}")
    # print()
    
    # ========================================================================
    # 8. Optional: Print Statistics
    # ========================================================================
    
    # print("Statistics:")
    # print(f"  Total events in trace: {len(sim.trace.events_list)}")
    # print(f"  Simulation time: {sim.current_time}")
    # print()
    
    # You can also inspect final states:
    # for pid in system.processes():
    #     state = sim.current_configuration[pid]
    #     print(f"  Process {pid}: {state}")


if __name__ == "__main__":
    main()

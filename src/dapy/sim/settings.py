from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Settings:
    """Configuration settings for a simulation.
    
    Attributes:
        is_verbose: Enable verbose output during simulation. Defaults to False.
        is_debug: Enable debug mode for detailed logging. Defaults to False.
        enable_trace: Enable trace recording for the simulation. Defaults to False.
    """
    is_verbose: bool = False
    is_debug: bool = False
    enable_trace: bool = False

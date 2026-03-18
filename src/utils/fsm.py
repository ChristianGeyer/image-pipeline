from time import perf_counter
from typing import Any

class FSM:
    """
    Simple finite state machine with timing.

    Tracks:
        - current state
        - time entering state (tes)
        - time in state (tis)

    State transitions reset timing automatically.
    """

    def __init__(self, initial_state: Any) -> None:
        self._state = initial_state
        self._tes = perf_counter()

    @property
    def state(self) -> Any:
        """Current state."""
        return self._state

    @property
    def tes(self) -> float:
        """Time of entering current state (absolute time)."""
        return self._tes

    @property
    def tis(self) -> float:
        """Time spent in current state (seconds)."""
        return perf_counter() - self._tes

    def update(self, new_state: Any) -> None:
        """
        Update the state.

        If the state changes, reset timing (tes).
        If the state is the same, do nothing.

        Args:
            new_state: The desired new state.
        """
        if new_state != self._state:
            self._state = new_state
            self._tes = perf_counter()

    def __repr__(self) -> str:
        return f"FSM(state={self._state}, tis={self.tis:.3f}s)"
    


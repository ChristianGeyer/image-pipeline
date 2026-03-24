from time import perf_counter
from typing import Any


class FSM:
    """
    Simple finite state machine (FSM) with timing support.

    This class tracks:
        - The current state
        - The time at which the current state was entered (tes)
        - The elapsed time spent in the current state (tis)

    When the state changes via `update`, the entry timestamp (tes) is reset.
    If the same state is provided, no changes are made.

    Typical usage:
        fsm = FSM(initial_state="IDLE")

        # Transition to a new state
        fsm.update("RUNNING")

        # Query current state and timing
        current = fsm.state
        time_in_state = fsm.tis
    """

    def __init__(self, initial_state: Any) -> None:
        """
        Initialize the FSM with an initial state.

        Args:
            initial_state: The starting state of the FSM (can be any type).
        """
        self._state = initial_state
        self._tes = perf_counter()

    @property
    def state(self) -> Any:
        """
        Current state of the FSM.

        Returns:
            The current state value.
        """
        return self._state

    @property
    def tes(self) -> float:
        """
        Time of entering the current state (absolute time).

        Returns:
            Timestamp (in seconds) from `time.perf_counter()` when the
            current state was entered.
        """
        return self._tes

    @property
    def tis(self) -> float:
        """
        Time spent in the current state.

        Returns:
            Elapsed time in seconds since the state was last entered.
        """
        return perf_counter() - self._tes

    def update(self, new_state: Any) -> None:
        """
        Update the FSM state.

        If `new_state` differs from the current state:
            - The state is updated
            - The entry timestamp (tes) is reset

        If `new_state` is the same as the current state:
            - No action is taken

        Args:
            new_state: The desired new state.
        """
        if new_state != self._state:
            self._state = new_state
            self._tes = perf_counter()

    def __repr__(self) -> str:
        """
        Return a string representation of the FSM.

        Includes:
            - Current state
            - Time in state (tis)

        Returns:
            String representation for debugging/logging.
        """
        return f"FSM(state={self._state}, tis={self.tis:.3f}s)"
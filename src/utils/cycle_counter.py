from time import perf_counter

class CycleCounter:
    """
    Track the number of cycles over time and compute frequency (Hz).

    A cycle can represent any repeated event (e.g., loop iteration, frame capture).
    """

    def __init__(self) -> None:
        self.reset()

    def tick(self, n: int = 1) -> None:
        """
        Increment the cycle count.

        Args:
            n: Number of cycles to add (default: 1).
        """
        self._count += n

    @property
    def count(self) -> int:
        """Return the number of recorded cycles."""
        return self._count

    @property
    def elapsed_time(self) -> float:
        """Return the elapsed time in seconds since last reset."""
        return perf_counter() - self._start_time

    @property
    def frequency(self) -> float:
        """
        Return the cycle frequency in Hz.

        Returns:
            Cycles per second. Returns 0.0 if elapsed time is zero.
        """
        elapsed = self.elapsed_time
        if elapsed <= 0:
            return 0.0
        return self._count / elapsed

    def reset(self) -> None:
        """Reset the counter and restart timing."""
        self._count = 0
        self._start_time = perf_counter()

    def snapshot(self) -> tuple[int, float, float]:
        """
        Return a snapshot of (count, elapsed_time, frequency).

        Returns:
            Tuple containing count, elapsed time (s), and frequency (Hz).
        """
        elapsed = self.elapsed_time
        freq = self.frequency
        return self._count, elapsed, freq

    def __repr__(self) -> str:
        return (
            f"CycleCounter(count={self._count}, "
            f"elapsed_time={self.elapsed_time:.4f}s, "
            f"frequency={self.frequency:.2f}Hz)"
        )
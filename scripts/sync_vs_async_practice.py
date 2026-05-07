import asyncio
import time


# These delays simulate network or disk waits.
# The point of the exercise is to compare waiting one-by-one vs waiting concurrently.
FAKE_IO_DELAYS = [1.0, 1.2, 0.8, 1.1, 0.9]


def fake_sync_io(task_id: int, delay: float) -> str:
    """Pretend to do blocking I/O work."""
    time.sleep(delay)
    
    return f"sync task {task_id} finished in {delay:.1f}s"

async def fake_async_io(task_id: int, delay: float) -> str:
    """Pretend to do non-blocking I/O work."""
    await asyncio.sleep(delay)
    
    return f"async task {task_id} finished in {delay:.1f}s"

def run_sync() -> list[str]:
    """Run all fake tasks sequentially."""
    results: list[str] = []

    for task_id, delay in enumerate(FAKE_IO_DELAYS, start=1):
        result = fake_sync_io(task_id, delay)
        results.append(result)

    return results

async def run_async() -> list[str]:
    """Run all fake tasks concurrently with asyncio.gather."""
    coroutines = []

    for task_id, delay in enumerate(FAKE_IO_DELAYS, start=1):
        coroutine = fake_async_io(task_id, delay)
        coroutines.append(coroutine)
        
    return await asyncio.gather(*coroutines)
    
def timed_sync_run() -> tuple[list[str], float]:
    """Measure how long the sequential version takes."""
    start = time.perf_counter()
    results = run_sync()
    duration = time.perf_counter() - start
    return results, duration


async def timed_async_run() -> tuple[list[str], float]:
    """Measure how long the async version takes."""
    start = time.perf_counter()
    results = await run_async()
    duration = time.perf_counter() - start
    return results, duration

def main() -> None:
    # TODO: run the sync version
    results_sync, duration_sync = timed_sync_run()
    results_async, duration_async = asyncio.run(timed_async_run())
    # TODO: print both result lists and durations
    print("Sequential run")
    for result in results_sync:
        print(f"- {result}")
    print(f"Total time: {duration_sync:.2f}s")

    print()
    print("Async run with gather")
    for result in results_async:
        print(f"- {result}")
    print(f"Total time: {duration_async:.2f}s")
    # TODO: print a one- or two-line takeaway about why async is faster here
    pass


if __name__ == "__main__":
    main()

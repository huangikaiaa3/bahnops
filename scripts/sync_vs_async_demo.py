import asyncio
import time


FAKE_IO_DELAYS = [1.0, 1.2, 0.8, 1.1, 0.9]


def fake_sync_io(task_id: int, delay: float) -> str:
    time.sleep(delay)
    return f"sync task {task_id} finished in {delay:.1f}s"


async def fake_async_io(task_id: int, delay: float) -> str:
    await asyncio.sleep(delay)
    return f"async task {task_id} finished in {delay:.1f}s"


def run_sync() -> list[str]:
    results = []
    for task_id, delay in enumerate(FAKE_IO_DELAYS, start=1):
        results.append(fake_sync_io(task_id, delay))
    return results


async def run_async() -> list[str]:
    coroutines = [
        fake_async_io(task_id, delay)
        for task_id, delay in enumerate(FAKE_IO_DELAYS, start=1)
    ]
    return await asyncio.gather(*coroutines)


def timed_sync_run() -> tuple[list[str], float]:
    start = time.perf_counter()
    results = run_sync()
    duration = time.perf_counter() - start
    return results, duration


async def timed_async_run() -> tuple[list[str], float]:
    start = time.perf_counter()
    results = await run_async()
    duration = time.perf_counter() - start
    return results, duration


def main() -> None:
    sync_results, sync_duration = timed_sync_run()
    async_results, async_duration = asyncio.run(timed_async_run())

    print("Sequential run")
    for result in sync_results:
        print(f"- {result}")
    print(f"Total time: {sync_duration:.2f}s")

    print()
    print("Async run with gather")
    for result in async_results:
        print(f"- {result}")
    print(f"Total time: {async_duration:.2f}s")

    print()
    print("Takeaway")
    print("- Sequential waits for each fake I/O task one by one.")
    print("- Async schedules all fake I/O tasks together and waits for the slowest one.")


if __name__ == "__main__":
    main()

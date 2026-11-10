import asyncio
import time

# first task
async def task1(delay: int):
    print("Task 1 is running...")
    await asyncio.sleep(delay)
    print("Task 1 is done.")

# second task
async def task2(delay: int):
    print("Task 2 is running...")
    time.sleep(delay) # This will block the execution of the program
    print("Task 2 is done.")

# third task
async def task3(delay: int):
    print("Task 3 is running...")
    await asyncio.sleep(delay)
    print("Task 3 is done.")

async def main():
    # Create tasks with Gather
    tasks = await asyncio.gather(
        task1(2),
        task2(4),
        task3(1)
    )

    print("All tasks are completed.")

asyncio.run(main())
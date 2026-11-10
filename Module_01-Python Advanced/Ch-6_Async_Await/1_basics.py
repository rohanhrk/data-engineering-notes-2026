import asyncio
import time

# co-routine function
async def async_function():
    print("Async function started") # This will print immediately
    await asyncio.sleep(2) # The thread will sleep for 2 seconds, but it won't block the execution of the program
    print("Async function ended") # # This will be executed right after the thread is idle

asyncio.run(async_function()) # This will run the async function in an event loop

def normal_function():
    print("Normal function started")
    time.sleep(2) # The thread will sleep for 2 seconds, blocking the execution of the program
    print("Normal function ended")

normal_function()
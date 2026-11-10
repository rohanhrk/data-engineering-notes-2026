import time

# def api_call():
#     print("API call started")
#     time.sleep(2) # Simulating a delay in API response
#     return "orders data"

# def execute_api_call():
#     print("Executing API call...")
#     data = api_call() # This will block the execution of the program until the API call is completed
#     print("API call completed")
#     return data

# data = execute_api_call()
# print(f"Received data: {data}")

import asyncio

async def api_call_async():
    print("Async API call started")
    await asyncio.sleep(3) # Simulating a delay in API response
    return "orders data"

async def execute_api_call_async():
    print("Executing async API call...")
    data = await api_call_async() # This will not block the execution of the program
    print("Async API call completed")
    return data

async def main():
    data = await execute_api_call_async()
    print(f"Received data: {data}")

asyncio.run(main())

"""
    Executing async API call...
    Async API call started
    Wait for 2 seconds...
    Async API call completed
    Received data: orders data

"""

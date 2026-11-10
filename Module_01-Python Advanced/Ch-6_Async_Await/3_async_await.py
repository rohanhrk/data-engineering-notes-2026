import time
import asyncio
# def inner_most():
#     print("Inner most function started")
#     time.sleep(2)
#     print("Inner most function ended")

# def inner():
#     print("Inner function started")
#     time.sleep(1)
#     inner_most()
#     print("Inner function ended")

# def outer_func():
#     print("Outer function started")
#     time.sleep(3)
#     inner()
#     print("Outer function ended")

# outer_func()

async def inner_most():
    print("Inner most function started")
    await asyncio.sleep(2)
    print("Inner most function ended")

async def inner():
    print("Inner function started")
    await asyncio.sleep(1)
    await inner_most()
    print("Inner function ended")

async def outer_func():
    print("Outer function started")
    await asyncio.sleep(3)
    await inner()
    print("Outer function ended")

asyncio.run(outer_func())
import asyncio

async def api_call_async(url:str, delay:int):
    print(f"Fetching data from {url}...")
    print(f"Wait for {delay} seconds...")
    await asyncio.sleep(delay) # Simulating a delay in API response
    print(f"Data fetched from {url}")
    return f"{url} data"

async def execute_multiple_api_calls():
    urls = [
        ("https://api.example.com/orders", 3),
        ("https://api.example.com/products", 2),
        ("https://api.example.com/customers", 1)
    ]
    
    tasks = [api_call_async(url, delay) for url, delay in urls]
    results = await asyncio.gather(*tasks) # This will run all the API calls concurrently
    return results

# To run the async function
async def main():
    results = await execute_multiple_api_calls()
    for result in results:
        print(result)

asyncio.run(main())
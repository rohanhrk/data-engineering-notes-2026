import time
from concurrent.futures import ThreadPoolExecutor

def fetch_data(url):
    print(f"Fetching data from {url}")
    time.sleep(2)  # Simulate a network delay
    print("Data fetched from:", url)
    return f"Data from {url}"

# Example usage
urls = ["http://example.com", "http://google.com", "http://github.com", "http://stackoverflow.com", "http://python.org"]

results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = executor.map(fetch_data, urls)
    results.extend(futures)
print("Results:", results)
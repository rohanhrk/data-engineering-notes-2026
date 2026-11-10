class APIFetch:
    def fetch(self):
        print("Fetching data from API...")

class DatabaseFatch:
    def fetch(self):
        print("Fetching data from Database...")

class S3Fetch:
    def fetch(self):
        print("Fetching data from S3...")

obj = DatabaseFatch()
DatabaseFatch.fetch(obj)
import requests

def api_call(url):
    response = requests.get(url)
    return {"data": response.json()}
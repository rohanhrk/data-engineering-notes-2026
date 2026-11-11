# Module 7 — Working with REST APIs

**Source folder:** `Ch-7_APIs/`  
**Source notebook reviewed:** `1_apis.ipynb`.

## 1. What is an API?

An API (Application Programming Interface) defines how one application requests data or actions from another. A REST-style API commonly exposes resources through HTTP methods and returns JSON.

A data engineer often extracts source data from APIs, handles pagination and authentication, validates responses, and writes data to a landing or Bronze layer.

## 2. Requests library and GET

The notebook imports `requests` and `json`. It sends a GET request to a JSONPlaceholder post endpoint.

```python
import requests
import json

url = "https://jsonplaceholder.typicode.com/posts/2"
response = requests.get(url)

print(response.status_code)
print(response.url)
print(response.headers)
data = response.json()
print(json.dumps(data, indent=2))
```

Useful response attributes/methods:
- `status_code`: HTTP status code.
- `url`: final request URL.
- `headers`: response headers.
- `json()`: decode a JSON response into Python objects.
- `text`: response body as text.
- `raise_for_status()`: raise an HTTP error for unsuccessful status codes.

A successful GET commonly returns status `200 OK`.

## 3. POST requests

The notebook demonstrates two request-body styles:

```python
payload = {"title": "foo", "body": "bar", "userId": 1}

response = requests.post(url, json=payload)
```

`json=` serializes a Python object as JSON and sets the appropriate content type.

```python
form_data = {"title": "xyz", "body": "abc", "userId": 1}
response = requests.post(url, data=form_data)
```

`data=` sends form-style data by default for a dictionary. Use the format required by the API contract.

A successful resource creation commonly returns `201 Created`.

## 4. Query parameters

The notebook uses `params` to construct URL query parameters:

```python
params = {"userId": 1, "id": 1}
response = requests.get(
    "https://jsonplaceholder.typicode.com/posts",
    params=params
)
```

Using `params=` is safer and clearer than manually concatenating query strings; the library handles URL encoding.

## 5. Headers and authentication

Headers carry metadata about the request. The notebook shows a custom User-Agent, Accept header, and custom header.

Common authentication patterns:

```python
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
}
response = requests.get(url, headers=headers)
```

Other examples shown in the notebook:
- API key in a header such as `X-API-Key`.
- Basic authentication via `requests.auth.HTTPBasicAuth`.

Never hard-code real credentials or commit tokens to Git. Use environment variables or a secret manager. The notebook's `token` is a placeholder and is not defined in the shown cell.

## 6. Production-ready API extraction pattern

```python
import requests

def fetch_json(url, params=None, headers=None):
    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
```

A production extractor should additionally consider:
- Retries with exponential backoff for transient errors.
- Rate limits and `Retry-After`.
- Pagination (page number, offset/limit, or cursor).
- Timeouts and connection reuse (`requests.Session`).
- Authentication token refresh.
- Logging request IDs and status codes without logging secrets.
- Schema validation and malformed-record handling.
- Incremental extraction using watermarks.

## 7. HTTP methods and status codes

The README describes GET, POST, PUT, and DELETE, but the retrieved notebook cells demonstrate GET, POST, query parameters, headers, and authentication. PUT and DELETE are mentioned in the course overview, but are not implemented in the notebook content reviewed.

| Method | Typical purpose |
|---|---|
| GET | Read/retrieve a resource |
| POST | Create or submit data |
| PUT | Replace/update a resource |
| PATCH | Partially update a resource |
| DELETE | Delete a resource |

Common status codes:
- `200`: success.
- `201`: created.
- `204`: success with no response body.
- `400`: bad request.
- `401`: unauthenticated.
- `403`: forbidden.
- `404`: not found.
- `429`: rate limited.
- `500` / `503`: server/service errors.

## 8. Data Engineering API ingestion flow

1. Read endpoint and credentials from configuration/secret storage.
2. Request a page or incremental time window.
3. Validate status and parse JSON.
4. Validate payload structure (for example with Pydantic).
5. Write raw response to a landing/Bronze location.
6. Track pagination or watermark state.
7. Log counts, latency, failures, and retries.

## 9. Common interview questions

1. **GET vs POST?** GET retrieves; POST submits data or creates resources.
2. **`json=` vs `data=` in requests?** JSON body serialization vs form/raw body handling.
3. **What are headers?** Request/response metadata.
4. **What is a query parameter?** A value in the URL query string used to filter or control a request.
5. **Why use `raise_for_status()`?** It surfaces unsuccessful HTTP responses as exceptions.
6. **What is pagination?** Splitting a large result set into manageable pages.
7. **How do you handle 429?** Respect rate-limit guidance, back off, and retry safely.
8. **How do you secure API keys?** Store them outside source code, preferably in a secret manager.

## 10. Revision checklist

- [ ] Make GET and POST requests.
- [ ] Explain `status_code`, `headers`, `url`, `json()`.
- [ ] Pass query parameters and custom headers.
- [ ] Explain Bearer, API-key, and Basic authentication.
- [ ] Add timeout and `raise_for_status()`.
- [ ] Explain pagination, retries, rate limits, and incremental extraction.

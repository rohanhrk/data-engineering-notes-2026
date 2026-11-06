# AWS Lambda External Dependencies Demo - City Weather Service

This project demonstrates how to package and deploy an AWS Lambda function with an external Python dependency (`requests`). Just send a city name and get weather info back.

## Use Case

This demo takes a city name and:
1. **Geocodes the city** — Calls Open-Meteo Geocoding API to convert city name to coordinates
2. **Fetches weather** — Calls Open-Meteo Weather API to get temperature, wind, sunrise/sunset

Since `requests` is not included in the Lambda Python runtime, it must be packaged with the code.

## File Structure

- `lambda_function.py`: The Lambda handler with geocoding and weather logic
- `requirements.txt`: External package (`requests`)
- `build.sh`: Automates packaging into a deployment-ready `.zip` file

## How to Package for AWS Lambda

### Prerequisites
- Python 3.x and `pip` installed locally

### Steps to Build
1. Open your terminal and navigate to this directory.
2. Make the script executable:
   ```bash
   chmod +x build.sh
   ```
3. Run the build script:
   ```bash
   ./build.sh
   ```

### What `build.sh` does:
1. Cleans up old build artifacts
2. Runs `pip3 install --target ./package -r requirements.txt` to download dependencies
3. Zips the `package/` folder + `lambda_function.py` into `deployment_package.zip`

## Deployment

Upload `deployment_package.zip` to your AWS Lambda function via the Console.
Set runtime to Python 3.12 or 3.13.

## Testing

### Test Event 1 — Simple city lookup
```json
{
  "city": "Mumbai"
}
```

### Test Event 2 — Another city
```json
{
  "city": "London"
}
```

### Expected Output
```json
{
  "statusCode": 200,
  "body": {
    "city": "Mumbai",
    "country": "India",
    "coordinates": { "latitude": 19.07283, "longitude": 72.88261 },
    "temperature_celsius": 32.5,
    "wind_speed_kmh": 15.2,
    "local_time": "2026-03-13T14:30",
    "sunrise": "2026-03-13T06:38",
    "sunset": "2026-03-13T18:38"
  }
}
```

### Test Event 3 — Missing city (error case)
```json
{}
```
Returns `400` with error: `"Missing 'city' in the request"`

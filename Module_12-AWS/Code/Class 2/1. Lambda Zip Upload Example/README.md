# Zipping steps

1. From the working directory, open the example folder:
   ```bash
   cd Lambda-Python-Example
   ```
2. Zip the handler and helper folder directly (without the enclosing example folder):
   ```bash
   zip -r lambda-deployment.zip lambda_function.py helpers -x '*/__pycache__/*' '*.pyc'
   ```

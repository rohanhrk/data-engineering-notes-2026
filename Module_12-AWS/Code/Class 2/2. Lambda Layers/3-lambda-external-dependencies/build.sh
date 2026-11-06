#!/bin/bash

# Exit on actual errors
set -e

echo "Starting build process for AWS Lambda deployment package..."

# 1. Clean up old build artifacts
echo "Cleaning up old build artifacts..."
rm -rf package
rm -f deployment_package.zip

# 2. Install dependencies to a local 'package' folder
echo "Installing external dependencies from requirements.txt..."
mkdir package
pip3 install --target ./package -r requirements.txt

# 3. Create a ZIP archive containing the dependencies
echo "Creating deployment package zip file..."
cd package
zip -r ../deployment_package.zip . > /dev/null
cd ..

# 4. Add the Lambda function code to the root of the ZIP archive
echo "Adding lambda_function.py to the deployment package..."
zip -g deployment_package.zip lambda_function.py > /dev/null

echo "========================================================"
echo "Deployment package 'deployment_package.zip' created successfully!"
echo "You can now upload this zip file to AWS Lambda."
echo "========================================================"

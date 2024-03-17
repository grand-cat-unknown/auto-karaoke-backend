#!/bin/bash

# Create a directory named 'package'
mkdir package

# Install dependencies in the 'package' directory
pip install --target ./package -r requirements.txt

# Create a .zip file with the installed libraries at the root
cd package
zip -r ../my_deployment_package.zip .

# Add the lambda_function.py file to the root of the .zip file
cd ..
zip my_deployment_package.zip lambda_function.py
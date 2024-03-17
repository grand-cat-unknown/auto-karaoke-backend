# Use the official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the local Lambda function code to the container
COPY . /app

# Install any dependencies
RUN pip install -r requirements.txt

# Command to run your Lambda function
CMD ["python", "lambda_function.py"]

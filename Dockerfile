# Use the official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the local Lambda function code to the container
COPY . /app

# Install any dependencies, including lxml
RUN apt-get update && apt-get install -y libxml2-dev libxslt-dev
RUN pip install -r requirements.txt

# Create a directory for lxml installation
RUN mkdir -p /opt/python/lxml

# Copy the contents of lxml_amazon_binaries to the container
COPY lxml_amazon_binaries /opt/python/lxml/

# Command to run your Lambda function
CMD ["python", "lambda_function.py"]
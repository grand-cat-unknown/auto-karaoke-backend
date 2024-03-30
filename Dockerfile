# Use AWS Lambda Python runtime as a parent image
FROM public.ecr.aws/lambda/python:3.9

# Set the working directory in the container
WORKDIR /var/task

# AWS Lambda base image is based on Amazon Linux, so we use yum instead of apt-get.
# However, libxml2 and libxslt should already be available in the AWS Lambda environment.
# If you absolutely need to install additional system packages, you would use yum. Example:
# RUN yum install -y <package-name>

# Copy the local Lambda function code and dependencies to the container
COPY . .

# Install Python dependencies, including lxml. There's no need to install lxml separately
# if it's already specified in your requirements.txt file.
RUN pip install -r requirements.txt

# If you have a specific reason for installing lxml separately and into a different directory
# within the Docker container, ensure that your Lambda function's code is correctly configured
# to use modules from this custom location. However, this is generally not necessary and
# can complicate your deployment without clear benefits for typical Lambda use cases.

# Note: The below command is an adaptation if you still need to go that route.
# It installs lxml into /var/task, which is the working directory,
# but this is generally not recommended unless you have a specific requirement.
RUN pip install lxml -t .

# Set the CMD to your handler (the AWS Lambda Python runtime expects a function handler)
CMD ["lambda_function.lambda_handler"]
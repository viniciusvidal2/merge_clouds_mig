# Use the official Ubuntu 22.04 as a base image
FROM ubuntu:22.04

# Set environment variables to avoid user interaction during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and other necessary packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip libgl1-mesa-glx libxrender1 xvfb && \
    apt-get clean
RUN pip3 install --upgrade pip

# Create the /app and /app/clouds directories, copy infrequent files
RUN mkdir -p /app /app/clouds
WORKDIR /app
COPY .streamlit /app/.streamlit

# Install required Python packages
COPY requirements/requirements.txt /app/requirements.txt
RUN pip3 install --no-cache -r requirements.txt

# Copy the rest of the application code to /app
COPY scripts /app/scripts
COPY app.py /app/

# Run the application
EXPOSE 8501
CMD ["streamlit", "run", "--server.port=8501", "--server.address=0.0.0.0", "app.py"]

FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files from the current directory to the container's working directory
COPY . .

# Install dependencies from the requirements file without using cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Expose the API port
EXPOSE 7860

# Start the application using Gunicorn with 4 worker processes
#   -w 4                 : 4 worker processes for handling requests
#   -b 0.0.0.0:7860      : bind to port 7860 on all interfaces
#   app:superkart_api    : run the Flask instance named superkart_api inside app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "--timeout", "120", "app:superkart_api"]

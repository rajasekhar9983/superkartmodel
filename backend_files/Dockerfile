
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r backend_files/requirements.txt

# Make port 7860 available to the world outside this container
EXPOSE 7860

# Run the Flask app
# The command 'gunicorn' is a production-ready WSGI HTTP server.
# '-b 0.0.0.0:7860' binds the server to all network interfaces on port 7860.
# 'app:app' refers to the 'app' variable (our Flask application instance)
# inside the 'app.py' module (which we will assume is our Flask application code).
# In this notebook, our Flask app is defined directly in cell Ti4Q3LcWwTBf
# For Docker, we would put the Flask app code into a file like app.py.
# Assuming the Flask app is saved as 'app.py' within the 'backend_files' directory.
CMD ["python", "-c", "from backend_files.app import app; app.run(host='0.0.0.0', port=7860)"]

# Note: For production deployments, gunicorn or uWSGI is recommended instead of app.run()
# CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"] # This would be used if app.py contains 'app = Flask(__name__)'
# For this Colab setup, running directly with Python for demonstration purposes.

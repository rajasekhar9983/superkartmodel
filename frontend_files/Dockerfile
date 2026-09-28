
# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app/frontend

# Copy the Streamlit app and requirements file
COPY app.py requirements.txt ./ 

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run the Streamlit app
# Streamlit runs on port 8501 by default
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

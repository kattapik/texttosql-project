# Use an official Python runtime as a parent image
FROM python:latest

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# (This build-time install serves as a baseline)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Initialize the database (Optional: if you want a fresh DB inside the container)
RUN python init_db.py 

# Set environment variables (Can be overridden at runtime)
# ENV GOOGLE_API_KEY=your_key_here
# ENV DB_PATH=sqlite.db

# Run init_db.py if DB is missing, then start the app
# Expose the port the app runs on
EXPOSE 8000

# Runtime command: 
# 1. Install/Update dependencies (Fast because of persistent volume)
# 2. Initialize DB if needed
# 3. Start Server
CMD ["sh", "-c", "pip install -r requirements.txt && if [ ! -f data/sqlite.db ]; then python init_db.py; fi && uvicorn server:server --host 0.0.0.0 --port 8000"]

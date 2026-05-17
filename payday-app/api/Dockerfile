# 1. Use a lightweight Python image as the foundation
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the requirements file first (Best practice for faster builds)
COPY requirements.txt .

# 4. Install the dependencies needed for the Payday API
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the application code
COPY . .

# 6. Tell Docker which port the API listens on
EXPOSE 5000

# 7. The command to start the API when the container launches
CMD ["python", "app.py"]

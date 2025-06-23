# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install required packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Run the bot
CMD ["python", "bot.py"]

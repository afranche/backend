# Use an official Python runtime as a parent image
FROM python:3.11

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
        libpq-dev  # Add any other system dependencies if needed

# Install Poetry
RUN pip install poetry

RUN poetry add gunicorn

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run app.py when the container launches
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:8080", "settings.wsgi:application"]

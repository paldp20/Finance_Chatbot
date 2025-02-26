FROM python:3
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#COPY ./utils.py /app/
COPY . .
CMD ["python", "-u", "fetcher.py"]

# # Start from a base Python image
# FROM python:3.9-slim

# # Set the working directory inside the container
# WORKDIR /app

# # Copy requirements and install dependencies
# COPY ./requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the source code for ticker-fetcher
# COPY ./fetcher.py /app/

# # Set the entrypoint (assuming ticker-fetcher.py is the entry point)
# CMD ["python", "fetcher.py"]

# # Copy the source code for ticker-fetcher
# COPY ./utils.py /app/

# # Set the entrypoint (assuming ticker-fetcher.py is the entry point)
# CMD ["python", "utils.py"]
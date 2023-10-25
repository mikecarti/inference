# Dockerfile for the helpDesk service
FROM python:3.10

WORKDIR /app/helpdesk

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Specify the command to run the helpDesk service
CMD [ "python3.10", "main.py"]
